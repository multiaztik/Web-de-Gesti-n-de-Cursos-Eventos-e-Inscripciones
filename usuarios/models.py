from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    """Extiende al usuario de Django con tipo de rol."""
    TIPO_CHOICES = [
        ('alumno', 'Alumno'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrador'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='alumno')

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.usuario.get_full_name() or self.usuario.username} ({self.get_tipo_display()})'

    def es_admin(self):
        return self.tipo == 'admin' or self.usuario.is_staff

    def es_instructor(self):
        return self.tipo == 'instructor'

    def es_alumno(self):
        return self.tipo == 'alumno'


class Alumno(models.Model):
    """Información académica del alumno vinculada a un usuario."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumno', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name='Nombre completo')
    correo = models.EmailField(unique=True, verbose_name='Correo electrónico')
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    foto = models.ImageField(upload_to='miembros/', blank=True, null=True, verbose_name='Foto')
    fecha_registro = models.DateField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.matricula})'


class Instructor(models.Model):
    """Información del instructor vinculada a un usuario."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name='Nombre completo')
    correo = models.EmailField(unique=True, verbose_name='Correo electrónico')
    especialidad = models.CharField(max_length=200, verbose_name='Especialidad')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')

    class Meta:
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
