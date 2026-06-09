from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario, Alumno, Instructor


class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro con nombre y correo para alumnos."""
    first_name = forms.CharField(
        max_length=100, label='Nombre', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100, label='Apellidos', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo electrónico', required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def clean_first_name(self):
        nombre = self.cleaned_data.get('first_name', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo electrónico.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            PerfilUsuario.objects.update_or_create(
                usuario=user,
                defaults={'tipo': 'alumno'}
            )
            # Crear perfil de Alumno asociado automáticamente
            Alumno.objects.create(
                usuario=user,
                nombre=f"{user.first_name} {user.last_name}".strip() or user.username,
                correo=user.email,
                matricula=f"AL{user.id:04d}",
                telefono=""
            )
        return user


class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'correo', 'matricula', 'telefono', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'foto': 'Opcional. No debe superar los 2 MB. Formatos: JPG, PNG, GIF, WebP.',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip()
        qs = Alumno.objects.filter(correo=correo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un alumno con este correo.')
        return correo

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto and hasattr(foto, 'size'):
            if foto.size > 2 * 1024 * 1024:
                raise forms.ValidationError('La imagen no debe superar los 2 MB.')
            if hasattr(foto, 'content_type') and foto.content_type not in [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp'
            ]:
                raise forms.ValidationError('Solo se permiten imágenes JPG, PNG, GIF o WebP.')
        return foto


class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['nombre', 'correo', 'especialidad', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip()
        qs = Instructor.objects.filter(correo=correo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un instructor con este correo.')
        return correo
