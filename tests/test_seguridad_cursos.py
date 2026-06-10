"""
Pruebas de integración: Seguridad y control de acceso — app cursos
===================================================================

Cubre los siguientes casos del checklist:
  ✔ Permisos de gestión de cursos: solo admin puede crear, editar o eliminar cursos.
    Alumno e instructor reciben HTTP 403 Forbidden.
"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cursos.models import Curso
from usuarios.models import Alumno, Instructor, PerfilUsuario


# ---------------------------------------------------------------------------
# Fixtures reutilizables
# ---------------------------------------------------------------------------

def crear_usuario_con_perfil(username, password, tipo):
    """Crea un User + PerfilUsuario con el rol indicado."""
    user = User.objects.create_user(username=username, password=password)
    PerfilUsuario.objects.create(usuario=user, tipo=tipo)
    return user


def crear_curso_base():
    """Crea un Curso activo de prueba."""
    return Curso.objects.create(
        nombre='Curso de Seguridad',
        descripcion='Descripción de prueba',
        fecha_inicio=datetime.date.today(),
        fecha_termino=datetime.date.today() + datetime.timedelta(days=30),
        cupo_maximo=15,
        estado='activo',
    )


# ---------------------------------------------------------------------------
# Test 4: Gestión de cursos — solo el admin puede crear, editar y eliminar
# ---------------------------------------------------------------------------

class PermisosCursoAdminTest(TestCase):
    """
    Pruebas de permisos para la administración de cursos.

    El objetivo es comprobar que únicamente los administradores puedan
    crear, editar o eliminar cursos. Los roles alumno e instructor no
    deben tener acceso a estas acciones.
    """

    def setUp(self):
        # Usuarios de los tres roles
        self.user_admin = crear_usuario_con_perfil('admin_cursos', 'pass1234', 'admin')
        self.user_alumno = crear_usuario_con_perfil('alumno_cursos', 'pass1234', 'alumno')
        self.user_instructor = crear_usuario_con_perfil('instructor_cursos', 'pass1234', 'instructor')

        # Curso existente para editar y eliminar
        self.curso = crear_curso_base()

    # -- Crear curso ----------------------------------------------------------

    def test_admin_puede_acceder_a_crear_curso(self):
        """
        Admin → GET /cursos/nuevo/ recibe HTTP 200 (ve el formulario).
        """
        self.client.login(username='admin_cursos', password='pass1234')
        url = reverse('curso_crear')
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder al formulario de creación de cursos',
        )

    def test_alumno_no_puede_acceder_a_crear_curso(self):
        """
        Alumno → GET /cursos/nuevo/ recibe HTTP 403 Forbidden.
        (UserPassesTestMixin con raise_exception=True lanza PermissionDenied)
        """
        self.client.login(username='alumno_cursos', password='pass1234')
        url = reverse('curso_crear')
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder acceder a la vista de crear cursos',
        )

    def test_instructor_no_puede_acceder_a_crear_curso(self):
        """
        Instructor → GET /cursos/nuevo/ recibe HTTP 403 Forbidden.
        """
        self.client.login(username='instructor_cursos', password='pass1234')
        url = reverse('curso_crear')
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder acceder a la vista de crear cursos',
        )

    # -- Editar curso ---------------------------------------------------------

    def test_admin_puede_acceder_a_editar_curso(self):
        """
        Admin → GET /cursos/<pk>/editar/ recibe HTTP 200.
        """
        self.client.login(username='admin_cursos', password='pass1234')
        url = reverse('curso_editar', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder al formulario de edición de cursos',
        )

    def test_alumno_no_puede_editar_curso(self):
        """
        Alumno → GET /cursos/<pk>/editar/ recibe HTTP 403 Forbidden.
        """
        self.client.login(username='alumno_cursos', password='pass1234')
        url = reverse('curso_editar', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder editar un curso',
        )

    def test_instructor_no_puede_editar_curso(self):
        """
        Instructor → GET /cursos/<pk>/editar/ recibe HTTP 403 Forbidden.
        """
        self.client.login(username='instructor_cursos', password='pass1234')
        url = reverse('curso_editar', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder editar un curso',
        )

    # -- Eliminar curso -------------------------------------------------------

    def test_admin_puede_acceder_a_eliminar_curso(self):
        """
        Admin → GET /cursos/<pk>/eliminar/ recibe HTTP 200 (página de confirmación).
        """
        self.client.login(username='admin_cursos', password='pass1234')
        url = reverse('curso_eliminar', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder a la confirmación de eliminación',
        )

    def test_alumno_no_puede_eliminar_curso(self):
        """
        Alumno → GET /cursos/<pk>/eliminar/ recibe HTTP 403 Forbidden.
        """
        self.client.login(username='alumno_cursos', password='pass1234')
        url = reverse('curso_eliminar', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder eliminar un curso',
        )

    def test_instructor_no_puede_eliminar_curso(self):
        """
        Instructor → GET /cursos/<pk>/eliminar/ recibe HTTP 403 Forbidden.
        """
        self.client.login(username='instructor_cursos', password='pass1234')
        url = reverse('curso_eliminar', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder eliminar un curso',
        )
