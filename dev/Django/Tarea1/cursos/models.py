from django.db import models


class Curso(models.Model):
    """Modelo que representa un Curso en el sistema."""
    nombre = models.CharField(max_length=200, verbose_name='Nombre del curso')
    descripcion = models.TextField(verbose_name='Descripción')
    instructor = models.CharField(max_length=150, verbose_name='Instructor')
    duracion_horas = models.PositiveIntegerField(verbose_name='Duración (horas)')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de fin')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
