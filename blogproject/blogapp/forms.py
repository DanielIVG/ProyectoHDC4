from django import forms
from .models import Blog
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class BlogForm(forms.ModelForm):
    contenido = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Blog
        fields = ['title', 'contenido', 'imagen']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Introduce una dirección de correo electrónico válida.',
        }
    )

    username = forms.CharField(
        required=True,
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'invalid': 'El nombre de usuario no es válido.',
        }
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        error_messages={
            'required': 'La contraseña es obligatoria.',
        }
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Por favor, confirma tu contraseña.',
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

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
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
