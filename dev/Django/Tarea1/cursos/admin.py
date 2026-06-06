from django.contrib import admin
from .models import Curso


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'instructor', 'duracion_horas', 'fecha_inicio', 'fecha_fin', 'activo')
    list_filter = ('activo', 'instructor')
    search_fields = ('nombre', 'instructor')
