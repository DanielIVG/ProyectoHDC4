from django import forms
from .models import Blog, Tag, Review
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # Cambiado para soportar subida de archivos
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class BlogForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorUploadingWidget(
            attrs={'class': 'bg-gray-800 text-white rounded-lg p-4'}
        ),
        label="Contenido"
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.MultipleHiddenInput  # El widget no afecta mucho porque lo manejas tú
    )

    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full',
                'placeholder': 'Ingresa el título del blog'
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-neon file:text-black hover:file:bg-neon/90'
            }),
            'tags': forms.MultipleHiddenInput(),
        }
        labels = {
            'title': 'Título',
            'image': 'Imagen destacada',
        }
        help_texts = {
            'image': 'Formatos soportados: JPG, PNG, WEBP (máx. 2MB)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].initial = 'Escribe aquí tu contenido...'
        self.fields['tags'].queryset = Tag.objects.all()
        #self.fields['tags'].widget = forms.HiddenInput()  # ← oculta el campo


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=Review.RATING_CHOICES, attrs={
                'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full h-32',
                'placeholder': 'Escribe tu reseña...'
            }),
        }
        labels = {
            'rating': 'Calificación',
            'comment': 'Comentario',
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full',
            'placeholder': 'correo@ejemplo.com'
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Introduce una dirección de correo electrónico válida.',
        }
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full',
            'placeholder': 'Nombre de usuario'
        }),
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'invalid': 'El nombre de usuario no es válido.',
        }
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full',
            'placeholder': '••••••••'
        }),
        error_messages={
            'required': 'La contraseña es obligatoria.',
        }
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full',
            'placeholder': '••••••••'
        }),
        error_messages={
            'required': 'Por favor, confirma tu contraseña.',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password)
        except ValidationError as e:
            translated_errors = []
            for error in e.messages:
                if "This password is too common." in error:
                    translated_errors.append("Esta contraseña es muy común.")
                elif "This password is entirely numeric." in error:
                    translated_errors.append("La contraseña no puede ser solo números.")
                elif "This password is too short." in error:
                    translated_errors.append("La contraseña es demasiado corta.")
                elif "too similar" in error:
                    translated_errors.append("La contraseña es muy similar a otros datos personales.")
                else:
                    translated_errors.append(error)
            raise ValidationError(translated_errors)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 w-full'
            }),
        }