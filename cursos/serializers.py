from rest_framework import serializers
from .models import Curso
from usuarios.models import Alumno, Instructor
from inscripciones.models import Inscripcion


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['id', 'nombre', 'correo', 'especialidad', 'telefono']


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


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ['id', 'nombre', 'correo', 'matricula', 'telefono', 'fecha_registro']


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
