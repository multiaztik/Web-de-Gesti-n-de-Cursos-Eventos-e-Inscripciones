from rest_framework import viewsets, permissions, status
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

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def inscritos(self, request, pk=None):
        """Endpoint extra: /api/cursos/{id}/inscritos/ (solo admin o instructor asignado)"""
        curso = self.get_object()
        
        # Validar permisos de la regla de negocio 6
        es_admin = False
        es_instructor_del_curso = False
        try:
            perfil = request.user.perfil
            es_admin = perfil.es_admin()
            if perfil.es_instructor():
                try:
                    es_instructor_del_curso = (curso.instructor == request.user.instructor)
                except Exception:
                    pass
        except Exception:
            es_admin = request.user.is_staff

        if not (es_admin or es_instructor_del_curso):
            return Response(
                {"detail": "No tienes permiso para ver esta información."},
                status=status.HTTP_403_FORBIDDEN
            )

        inscripciones = Inscripcion.objects.filter(curso=curso).select_related('alumno')
        serializer = InscripcionSerializer(inscripciones, many=True)
        return Response(serializer.data)


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir que solo los dueños de un objeto
    o los administradores lo editen.
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para cualquier petición segura (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permitir si el usuario es administrador
        if request.user and (request.user.is_staff or (hasattr(request.user, 'perfil') and request.user.perfil.es_admin())):
            return True
            
        # Validar si es el alumno dueño del perfil
        if isinstance(obj, Alumno) and obj.usuario == request.user:
            return True
            
        # Validar si es el instructor dueño del perfil
        if isinstance(obj, Instructor) and obj.usuario == request.user:
            return True
            
        # Validar si es el alumno dueño de la inscripción
        if isinstance(obj, Inscripcion) and obj.alumno.usuario == request.user:
            return True
            
        return False


class AlumnoViewSet(viewsets.ModelViewSet):
    """API REST para alumnos."""
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly]


class InscripcionViewSet(viewsets.ModelViewSet):
    """API REST para inscripciones."""
    queryset = Inscripcion.objects.select_related('alumno', 'curso').all()
    serializer_class = InscripcionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly]


class InstructorViewSet(viewsets.ModelViewSet):
    """API REST para instructores."""
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly]
