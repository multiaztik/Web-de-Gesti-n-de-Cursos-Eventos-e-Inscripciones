from django.db import models
from usuarios.models import Alumno
from cursos.models import Curso


class Inscripcion(models.Model):
    """Relación muchos a muchos entre Alumno y Curso con datos extra."""
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    alumno = models.ForeignKey(
        Alumno, on_delete=models.CASCADE, related_name='inscripciones', verbose_name='Alumno'
    )
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='inscripciones', verbose_name='Curso'
    )
    fecha_inscripcion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inscripción')
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='activa', verbose_name='Estado'
    )
    evidencia = models.FileField(
        upload_to='inscripciones/evidencias/', blank=True, null=True,
        verbose_name='Comprobante de inscripción'
    )

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        unique_together = ('alumno', 'curso')  # RF09: evitar duplicados
        ordering = ['-fecha_inscripcion']

    def __str__(self):
        return f'{self.alumno} → {self.curso}'
