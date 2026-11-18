from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.schema import AUTH_ERRORS, E400, E401, E404, E429

from .models import User
from .permissions import IsAdminRole
from .serializers import (
    AdminUserSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

TAG = "Kimlik doğrulama"
AuthResponse = inline_serializer(
    name="OturumYaniti",
    fields={
        "user": UserSerializer(),
        "access": serializers.CharField(help_text="Erişim anahtarı (30 dk). Authorize düğmesine bu yapıştırılır."),
        "refresh": serializers.CharField(help_text="Yenileme anahtarı (7 gün)."),
    },
)


@extend_schema(
    tags=[TAG],
    summary="Kayıt ol",
    description="Yeni ebeveyn hesabı açar; aile ve varsayılan koruma politikası otomatik oluşturulur. Oturum anahtarları döner.",
    auth=[],
    responses={201: AuthResponse, 400: E400, 429: E429},
)
class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — yeni ebeveyn hesabı açar ve oturum anahtarlarını döndürür."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {"user": UserSerializer(user).data, "access": str(refresh.access_token), "refresh": str(refresh)},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=[TAG],
    summary="Giriş yap",
    description="E-posta ve şifreyle giriş yapar. Dönen `access` anahtarını sağ üstteki **Authorize** düğmesine yapıştırın.",
    auth=[],
    responses={200: AuthResponse, 400: E400, 401: E401, 429: E429},
)
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    throttle_scope = "auth"


@extend_schema(
    tags=[TAG],
    summary="Oturumu yenile",
    description="Süresi dolan erişim anahtarı yerine `refresh` anahtarıyla yenisini alır.",
    auth=[],
    responses={200: inline_serializer("YenilemeYaniti", {"access": serializers.CharField(), "refresh": serializers.CharField()}), 401: E401},
)
class RefreshView(TokenRefreshView):
    pass


@extend_schema(tags=[TAG], summary="Çıkış yap", request=None, responses={204: None, 401: E401})
class LogoutView(APIView):
    """Refresh anahtarını kara listeye almak yerine istemci tarafında silinmesi yeterlidir;
    bu uç nokta oturum kapatmanın API üzerinden de yapılabilmesi için vardır."""

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(tags=[TAG], summary="Profilimi getir", responses={200: UserSerializer, 401: E401}),
    put=extend_schema(tags=[TAG], summary="Profilimi güncelle", responses={200: UserSerializer, 400: E400, 401: E401}),
    patch=extend_schema(tags=[TAG], summary="Profilimi kısmen güncelle", responses={200: UserSerializer, 400: E400, 401: E401}),
)
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=[TAG],
    summary="Şifre değiştir",
    request=ChangePasswordSerializer,
    responses={200: inline_serializer("SifreYaniti", {"detail": serializers.CharField()}), 400: E400, 401: E401},
)
class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Şifreniz güncellendi."})


@extend_schema_view(
    list=extend_schema(summary="Kullanıcıları listele", description="`?search=` ile e-posta/ad araması, `?role=parent|admin` ile rol filtresi."),
    create=extend_schema(summary="Kullanıcı oluştur", responses={201: AdminUserSerializer, 400: E400, **AUTH_ERRORS}),
    retrieve=extend_schema(summary="Kullanıcı ayrıntısı", responses={200: AdminUserSerializer, 404: E404, **AUTH_ERRORS}),
    update=extend_schema(summary="Kullanıcıyı güncelle", responses={200: AdminUserSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    partial_update=extend_schema(summary="Kullanıcıyı kısmen güncelle", responses={200: AdminUserSerializer, 400: E400, 404: E404, **AUTH_ERRORS}),
    destroy=extend_schema(summary="Kullanıcıyı sil", description="Yönetici kendi hesabını silemez (400).", responses={204: None, 400: E400, 404: E404, **AUTH_ERRORS}),
)
@extend_schema(tags=["Yönetim"])
class AdminUserViewSet(viewsets.ModelViewSet):
    """Yönetici: tüm kullanıcılar üzerinde CRUD."""

    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        qs = User.objects.select_related("family").all()
        search = self.request.query_params.get("search")
        role = self.request.query_params.get("role")
        if search:
            qs = qs.filter(Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
        if role:
            qs = qs.filter(role=role)
        return qs

    def destroy(self, request, *args, **kwargs):
        if self.get_object() == request.user:
            return Response(
                {"detail": "Kendi hesabınızı silemezsiniz.", "errors": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
