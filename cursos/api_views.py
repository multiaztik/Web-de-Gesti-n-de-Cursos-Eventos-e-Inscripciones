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


class IsAdminOrInstructorOrSelf(permissions.BasePermission):
    """
    Permiso para AlumnoViewSet:
    - Administradores e Instructores tienen acceso de lectura (GET/list/detail).
    - Alumnos solo pueden ver/editar su propia información de alumno (GET/detail, PUT, PATCH).
    - Anónimos no tienen acceso.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if view.action == 'list':
            try:
                return request.user.is_staff or request.user.perfil.es_admin() or request.user.perfil.es_instructor()
            except Exception:
                return request.user.is_staff
        
        return True

    def has_object_permission(self, request, view, obj):

        try:
            if request.user.is_staff or request.user.perfil.es_admin() or request.user.perfil.es_instructor():
                return True
        except Exception:
            if request.user.is_staff:
                return True

        return obj.usuario == request.user


class IsAdminOrSelfOrReadOnlyAuthenticated(permissions.BasePermission):
    """
    Permiso para InstructorViewSet:
    - Debe estar autenticado (no anónimos).
    - Lectura permitida para cualquier usuario autenticado.
    - Modificación (PUT, PATCH) permitida solo a sí mismo (el instructor dueño) o al administrador.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        try:
            if request.user.is_staff or request.user.perfil.es_admin():
                return True
        except Exception:
            if request.user.is_staff:
                return True
                
        return obj.usuario == request.user


class IsInscripcionOwnerOrInstructorOrAdmin(permissions.BasePermission):
    """
    Permiso para InscripcionViewSet:
    - Debe estar autenticado.
    - Creación (POST): Alumnos solo pueden inscribirse a sí mismos.
    - Edición (PUT, PATCH): Solo el alumno dueño puede modificar o el Admin.
    - Detalle (GET): Solo el dueño de la inscripción, el instructor del curso, o el Admin.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
    
        if view.action == 'create':
            try:
                if request.user.is_staff or request.user.perfil.es_admin():
                    return True
            except Exception:
                pass

            alumno_id = request.data.get('alumno')
            if not alumno_id:
                return True 
            
            try:
                alumno = Alumno.objects.get(id=alumno_id)
                return alumno.usuario == request.user
            except Alumno.DoesNotExist:
                return False
                
        return True

    def has_object_permission(self, request, view, obj):

        try:
            if request.user.is_staff or request.user.perfil.es_admin():
                return True
        except Exception:
            if request.user.is_staff:
                return True

        if request.method in permissions.SAFE_METHODS:
            is_owner = (obj.alumno.usuario == request.user)
            is_instructor = (obj.curso.instructor and obj.curso.instructor.usuario == request.user)
            return is_owner or is_instructor
            
        # Si es modificación, solo el alumno dueño
        return obj.alumno.usuario == request.user


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

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsAdminOrInstructorOrSelf()]


class InscripcionViewSet(viewsets.ModelViewSet):
    """API REST para inscripciones."""
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Inscripcion.objects.none()
        
        try:
            if user.is_staff or user.perfil.es_admin():
                return Inscripcion.objects.select_related('alumno', 'curso').all()
            elif user.perfil.es_instructor():
                return Inscripcion.objects.filter(curso__instructor__usuario=user).select_related('alumno', 'curso')
            elif user.perfil.es_alumno():
                return Inscripcion.objects.filter(alumno__usuario=user).select_related('alumno', 'curso')
        except Exception:
            if user.is_staff:
                return Inscripcion.objects.select_related('alumno', 'curso').all()
        
        return Inscripcion.objects.none()

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsInscripcionOwnerOrInstructorOrAdmin()]


class InstructorViewSet(viewsets.ModelViewSet):
    """API REST para instructores."""
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsAdminOrSelfOrReadOnlyAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Instructor eliminado exitosamente."},
            status=status.HTTP_200_OK
        )

