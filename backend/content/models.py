from django.db import models


class FAQ(models.Model):
    """Tanıtım sitesindeki Sıkça Sorulan Sorular; yönetici panelinden yönetilir."""

    question = models.CharField("soru", max_length=200)
    answer = models.TextField("cevap")
    order = models.PositiveSmallIntegerField("sıra", default=0)
    is_published = models.BooleanField("yayında", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "SSS"
        verbose_name_plural = "SSS"

    def __str__(self) -> str:
        return self.question


class ContactRequest(models.Model):
    """Ziyaretçilerin iletişim / demo talepleri."""

    class Topic(models.TextChoices):
        DEMO = "demo", "Demo talebi"
        SUPPORT = "support", "Destek"
        PARTNERSHIP = "partnership", "İş birliği"
        OTHER = "other", "Diğer"

    class Status(models.TextChoices):
        NEW = "new", "Yeni"
        IN_PROGRESS = "in_progress", "İnceleniyor"
        RESOLVED = "resolved", "Çözüldü"

    name = models.CharField("ad soyad", max_length=100)
    email = models.EmailField("e-posta")
    topic = models.CharField(max_length=20, choices=Topic.choices, default=Topic.DEMO)
    message = models.TextField("mesaj", max_length=2000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    admin_note = models.TextField("yönetici notu", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "iletişim talebi"
        verbose_name_plural = "iletişim talepleri"

    def __str__(self) -> str:
        return f"{self.name} - {self.get_topic_display()}"
