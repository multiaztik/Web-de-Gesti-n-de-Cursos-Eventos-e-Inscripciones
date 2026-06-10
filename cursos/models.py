from django.db import models
from usuarios.models import Instructor


class Curso(models.Model):
    """Representa un curso o evento académico."""
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('cerrado', 'Cerrado'),
        ('cancelado', 'Cancelado'),
    ]

    nombre = models.CharField(max_length=200, verbose_name='Nombre del curso')
    descripcion = models.TextField(verbose_name='Descripción')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_termino = models.DateField(verbose_name='Fecha de término')
    cupo_maximo = models.PositiveIntegerField(verbose_name='Cupo máximo')
    instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cursos', verbose_name='Instructor'
    )
    imagen = models.ImageField(
        upload_to='cursos/imagenes/', blank=True, null=True, verbose_name='Imagen o archivo'
    )
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='activo', verbose_name='Estado'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def cupo_disponible(self):
        """Retorna cuántos lugares quedan."""
        inscritos = self.inscripciones.filter(estado='activo').count()
        return self.cupo_maximo - inscritos

    def tiene_cupo(self):
        return self.cupo_disponible() > 0

    def acepta_inscripciones(self):
        return self.estado == 'activo' and self.tiene_cupo()

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        if self.fecha_inicio and self.fecha_termino and self.fecha_termino < self.fecha_inicio:
            raise ValidationError(
                {'fecha_termino': 'La fecha de término no puede ser anterior a la fecha de inicio.'}
            )
