from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    FileExtensionValidator
)
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField

# ---- Validación personalizada para imágenes ----
def validate_image_size(value):
    """Limita el tamaño de imágenes a 2MB."""
    limit = 10 * 1024 * 1024  # 2MB
    if value and value.size > limit:
        raise ValidationError('La imagen no puede superar 2MB de tamaño.')

# ---- Modelo Blog ----
class Blog(models.Model):
    title = models.CharField(
        "Título del Blog",
        max_length=255,
        help_text="Ingrese un título descriptivo (máx. 255 caracteres)"
    )
    content = RichTextField(
        "Contenido",
        default='Escribe aquí tu contenido...'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Autor"
    )
    created_at = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )
    tag = models.CharField(
        "Etiqueta",
        max_length=50,
        blank=True,
        null=True,
        help_text="Etiqueta para categorización (opcional)"
    )
    imagen = models.ImageField(
        "Imagen destacada",
        upload_to='blog_images/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size
        ],
        help_text="Formatos soportados: JPG, PNG (máx. 2MB)"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Entrada de Blog"
        verbose_name_plural = "Entradas de Blog"
        indexes = [
            models.Index(fields=['title']),  # Índice para búsquedas
        ]
        ordering = ['-created_at']  # Orden descendente por fecha

# ---- Modelo Review ----
class Review(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Blog asociado"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Revisor"
    )
    rating = models.IntegerField(
        "Calificación",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
        help_text="Valor entre 1 (peor) y 5 (mejor)"
    )
    comment = models.TextField(
        "Comentario",
        help_text="Escribe tu opinión detallada"
    )
    created_at = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.reviewer.username} - {self.blog.title}"

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"

# ---- Modelo Comment ----
class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Reseña asociada"
    )
    commenter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Comentarista"
    )
    content = models.TextField(
        "Contenido",
        help_text="Escribe tu comentario"
    )
    created_at = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )

    def __str__(self):
        return f"Comment by {self.commenter.username}"

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

    class UserProfile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE)
        image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

        def __str__(self):
            return self.user.username
