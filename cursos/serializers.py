from rest_framework import serializers
from .models import Curso
from usuarios.models import Alumno, Instructor
from inscripciones.models import Inscripcion


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['id', 'nombre', 'correo', 'especialidad', 'telefono']
        extra_kwargs = {
            'nombre': {'min_length': 3}
        }


class CursoSerializer(serializers.ModelSerializer):
    instructor_nombre = serializers.CharField(source='instructor.nombre', read_only=True)
    cupo_disponible = serializers.IntegerField(read_only=True)

    class Meta:
        model = Curso
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_termino',
            'cupo_maximo', 'cupo_disponible', 'instructor', 'instructor_nombre',
            'estado', 'imagen',
        ]
        extra_kwargs = {
            'nombre': {'min_length': 3}
        }

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_termino = data.get('fecha_termino')
        if fecha_inicio and fecha_termino and fecha_termino < fecha_inicio:
            raise serializers.ValidationError(
                'La fecha de término no puede ser anterior a la fecha de inicio.'
            )
        return data

    def validate_cupo_maximo(self, value):
        if value <= 0:
            raise serializers.ValidationError('El cupo máximo debe ser mayor que cero.')
        return value

    def validate_imagen(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError('La imagen no debe superar los 5 MB.')
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise serializers.ValidationError(
                    'Solo se permiten imágenes JPG, PNG, GIF o WebP.'
                )
        return value


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ['id', 'nombre', 'correo', 'matricula', 'telefono', 'fecha_registro']
        extra_kwargs = {
            'nombre': {'min_length': 3}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user:
            is_admin = request.user.is_staff
            try:
                if hasattr(request.user, 'perfil') and request.user.perfil.es_admin():
                    is_admin = True
            except Exception:
                pass
            if not is_admin:
                self.fields['matricula'].read_only = True

    def validate_foto(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError('La imagen no debe superar los 2 MB.')
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise serializers.ValidationError(
                    'Solo se permiten imágenes JPG, PNG, GIF o WebP.'
                )
        return value



class InscripcionSerializer(serializers.ModelSerializer):
    alumno_nombre = serializers.CharField(source='alumno.nombre', read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)

    class Meta:
        model = Inscripcion
        fields = ['id', 'alumno', 'alumno_nombre', 'curso', 'curso_nombre',
                  'fecha_inscripcion', 'estado', 'evidencia']
        read_only_fields = ['fecha_inscripcion']

    def validate(self, data):
        curso = data.get('curso')
        # Solo validar al crear una nueva inscripción (no al actualizar)
        if not self.instance:
            if curso.estado == 'cancelado':
                raise serializers.ValidationError('Este curso está cancelado y no acepta inscripciones.')
            if curso.estado == 'cerrado':
                raise serializers.ValidationError('Este curso está cerrado y no acepta inscripciones.')
            if not curso.tiene_cupo():
                raise serializers.ValidationError('Lo sentimos, el curso ha alcanzado su cupo máximo.')
        return data

    def validate_evidencia(self, value):
        if value:
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError('El archivo no debe superar los 10 MB.')
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx']:
                raise serializers.ValidationError(
                    'Extensión de archivo no permitida. Solo se permiten archivos PDF, imágenes o Word.'
                )
        return value
