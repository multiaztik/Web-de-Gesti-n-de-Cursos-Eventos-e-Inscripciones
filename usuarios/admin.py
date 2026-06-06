from django.contrib import admin
from .models import PerfilUsuario, Alumno, Instructor


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo')
    list_filter = ('tipo',)


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'matricula', 'correo', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'matricula', 'correo')


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'especialidad', 'telefono')
    search_fields = ('nombre', 'especialidad')
