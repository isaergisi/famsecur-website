from django.db.models import Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .permissions import IsAdminRole
from .serializers import (
    AdminUserSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
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


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    throttle_scope = "auth"


class LogoutView(APIView):
    """Refresh anahtarını kara listeye almak yerine istemci tarafında silinmesi yeterlidir;
    bu uç nokta oturum kapatmanın API üzerinden de yapılabilmesi için vardır."""

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Şifreniz güncellendi."})


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
