from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Curso
from usuarios.models import Alumno, Instructor
from inscripciones.models import Inscripcion
from .serializers import (
    CursoSerializer, AlumnoSerializer, InscripcionSerializer, InstructorSerializer
)


class IsAdminOrCourseInstructor(permissions.BasePermission):
    """
    Permiso que autoriza únicamente al administrador o al instructor
    que imparte el curso específico.
    """
    def has_object_permission(self, request, view, obj):
        from django.core.exceptions import ObjectDoesNotExist
        # 1. Verificar si el usuario está autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Verificar si es administrador
        try:
            if request.user.is_staff or request.user.perfil.es_admin():
                return True
        except (AttributeError, ObjectDoesNotExist):
            if request.user.is_staff:
                return True

        # 3. Verificar si es el instructor del curso (el objeto 'obj' es una instancia de Curso)
        try:
            return obj.instructor == request.user.instructor
        except (AttributeError, ObjectDoesNotExist):
            return False


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir que solo los dueños de un objeto
    o los administradores lo editen.
    """
    def has_object_permission(self, request, view, obj):
        from django.core.exceptions import ObjectDoesNotExist
        # Lectura permitida para cualquier petición segura (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permitir si el usuario es administrador
        try:
            if request.user and (request.user.is_staff or request.user.perfil.es_admin()):
                return True
        except (AttributeError, ObjectDoesNotExist):
            if request.user and request.user.is_staff:
                return True
            
        # Comprobar propiedad basándose en atributos comunes del objeto
        # Caso 1: El objeto tiene directamente un atributo 'usuario' (e.g. Alumno, Instructor)
        usuario_propietario = getattr(obj, 'usuario', None)
        if usuario_propietario and usuario_propietario == request.user:
            return True
            
        # Caso 2: El objeto tiene un atributo 'alumno' (e.g. Inscripcion)
        alumno_relacionado = getattr(obj, 'alumno', None)
        if alumno_relacionado:
            usuario_alumno = getattr(alumno_relacionado, 'usuario', None)
            if usuario_alumno and usuario_alumno == request.user:
                return True
            
        return False


class CursoViewSet(viewsets.ModelViewSet):
    """API REST para cursos: GET, POST, PUT, PATCH, DELETE."""
    queryset = Curso.objects.select_related('instructor').all()
    serializer_class = CursoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminOrCourseInstructor])
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
