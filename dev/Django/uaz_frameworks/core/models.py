from django.db import models

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Miembro(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    cursos = models.ManyToManyField(Curso, blank=True)
    foto = models.ImageField(upload_to='fotos/', blank=True, null=True)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)

    def __str__(self):
        return self.nombre