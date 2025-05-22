from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    FileExtensionValidator
)
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField


class Tag(models.Model):
    name = models.CharField(
        "Nombre del Tag",
        max_length=50,
        unique=True,
        help_text="Nombre único para la categorización"
    )
    color = models.CharField(
        "Color del Tag",
        max_length=7,
        default="#3B82F6",
        help_text="Color en formato HEX (ej: #3B82F6)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ['name']


# Validación personalizada para imágenes
def validate_image_size(value):
    """Limita el tamaño de imágenes a 2MB."""
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('La imagen no puede superar 2MB de tamaño.')


class Blog(models.Model):
    title = models.CharField(
        "Título del Blog",
        max_length=255,
        help_text="Ingrese un título descriptivo (máx. 255 caracteres)"
    )
    content = RichTextUploadingField(
        "Contenido",
        default='Escribe aquí tu contenido...',
        help_text="Editor completo con soporte para imágenes"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Autor",
        related_name='blogs'
    )
    created_at = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True
    )
    image = models.ImageField(
        "Imagen destacada",
        upload_to='blog_images/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size
        ],
        help_text="Formatos soportados: JPG, PNG, WEBP (máx. 2MB)"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Entrada de Blog"
        verbose_name_plural = "Entradas de Blog"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']


class Review(models.Model):
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]

    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Blog asociado"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Revisor",
        related_name='reviews'
    )
    rating = models.IntegerField(
        "Calificación",
        choices=RATING_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
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
        return f"Reseña de {self.reviewer.username} para {self.blog.title}"

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        unique_together = ['blog', 'reviewer']  # Un usuario solo puede reseñar una vez
        ordering = ['-created_at']


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
        verbose_name="Comentarista",
        related_name='comments'
    )
    content = models.TextField(
        "Contenido",
        help_text="Escribe tu comentario"
    )
    created_at = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )
    
    # Campo de likes
    likes = models.ManyToManyField(
        User,
        related_name='liked_comments',
        blank=True,
        verbose_name="Usuarios que dieron me gusta"
    )

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Comentario de {self.commenter.username}"

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['created_at']
