from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Curso
from usuarios.models import Alumno, Instructor
from inscripciones.models import Inscripcion
from .serializers import (
    CursoSerializer, AlumnoSerializer, InscripcionSerializer, InstructorSerializer
)


class CursoViewSet(viewsets.ModelViewSet):
    """API REST para cursos: GET, POST, PUT, PATCH, DELETE."""
    queryset = Curso.objects.select_related('instructor').all()
    serializer_class = CursoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['get'])
    def inscritos(self, request, pk=None):
        """Endpoint extra: /api/cursos/{id}/inscritos/"""
        curso = self.get_object()
        inscripciones = Inscripcion.objects.filter(curso=curso).select_related('alumno')
        serializer = InscripcionSerializer(inscripciones, many=True)
        return Response(serializer.data)


class AlumnoViewSet(viewsets.ModelViewSet):
    """API REST para alumnos."""
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class InscripcionViewSet(viewsets.ModelViewSet):
    """API REST para inscripciones."""
    queryset = Inscripcion.objects.select_related('alumno', 'curso').all()
    serializer_class = InscripcionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class InstructorViewSet(viewsets.ModelViewSet):
    """API REST para instructores."""
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
