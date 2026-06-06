from django.contrib import admin
from .models import Curso


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'instructor', 'estado', 'cupo_maximo', 'fecha_inicio', 'fecha_termino')
    list_filter = ('estado', 'instructor')
    search_fields = ('nombre', 'instructor__nombre')
    date_hierarchy = 'fecha_inicio'
