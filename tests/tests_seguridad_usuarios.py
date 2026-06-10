"""
Pruebas de integración: Seguridad y control de acceso — app usuarios
=====================================================================

Cubre los siguientes casos del checklist:
  ✔ Permisos del CRUD de Alumnos: solo admin puede crear/editar/eliminar alumnos.
  ✔ Permisos del CRUD de Instructores: solo admin puede crear/editar/eliminar instructores.
  ✔ Cierre de sesión (Backend): logout destruye la sesión activa del usuario.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Alumno, Instructor, PerfilUsuario


# ---------------------------------------------------------------------------
# Fixtures reutilizables
# ---------------------------------------------------------------------------

def crear_usuario_con_perfil(username, password, tipo):
    """Crea un User + PerfilUsuario con el rol indicado."""
    user = User.objects.create_user(username=username, password=password)
    PerfilUsuario.objects.create(usuario=user, tipo=tipo)
    return user


def crear_alumno_de_prueba(n=1):
    """Crea un Alumno sin usuario vinculado para usar como objetivo de edición/eliminación."""
    return Alumno.objects.create(
        nombre=f'Alumno Objetivo {n}',
        correo=f'objetivo{n}@test.com',
        matricula=f'OBJ{n:03d}',
    )


def crear_instructor_de_prueba(n=1):
    """Crea un Instructor sin usuario vinculado para usar como objetivo."""
    return Instructor.objects.create(
        nombre=f'Instructor Objetivo {n}',
        correo=f'instructor_obj{n}@test.com',
        especialidad='Matemáticas',
    )


# ---------------------------------------------------------------------------
# Test 5a: CRUD de Alumnos — solo el admin tiene permiso
# ---------------------------------------------------------------------------

class PermisosAlumnoCRUDTest(TestCase):
    """
    Pruebas de permisos para el CRUD de alumnos.

    Se verifica que únicamente los usuarios con rol admin puedan crear,
    editar y eliminar alumnos. Los usuarios alumno e instructor deben
    recibir un error 403 al intentar acceder a estas acciones.
    """

    def setUp(self):
        self.user_admin = crear_usuario_con_perfil('admin_alumnos', 'pass1234', 'admin')
        self.user_alumno = crear_usuario_con_perfil('alumno_normal', 'pass1234', 'alumno')
        self.user_instructor = crear_usuario_con_perfil('instructor_normal', 'pass1234', 'instructor')

        # Alumno existente para las pruebas de editar/eliminar
        self.alumno_objetivo = crear_alumno_de_prueba(1)

    # -- Crear alumno ---------------------------------------------------------

    def test_admin_puede_crear_alumno(self):
        """Admin → GET /usuarios/alumnos/nuevo/ recibe HTTP 200."""
        self.client.login(username='admin_alumnos', password='pass1234')
        respuesta = self.client.get(reverse('alumno_crear'))

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder al formulario de creación de alumnos',
        )

    def test_alumno_no_puede_crear_alumno(self):
        """Alumno → GET /usuarios/alumnos/nuevo/ recibe HTTP 403."""
        self.client.login(username='alumno_normal', password='pass1234')
        respuesta = self.client.get(reverse('alumno_crear'))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder acceder a la creación de alumnos',
        )

    def test_instructor_no_puede_crear_alumno(self):
        """Instructor → GET /usuarios/alumnos/nuevo/ recibe HTTP 403."""
        self.client.login(username='instructor_normal', password='pass1234')
        respuesta = self.client.get(reverse('alumno_crear'))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder acceder a la creación de alumnos',
        )

    # -- Editar alumno --------------------------------------------------------

    def test_admin_puede_editar_alumno(self):
        """Admin → GET /usuarios/alumnos/<pk>/editar/ recibe HTTP 200."""
        self.client.login(username='admin_alumnos', password='pass1234')
        respuesta = self.client.get(reverse('alumno_editar', args=[self.alumno_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder al formulario de edición de alumnos',
        )

    def test_alumno_no_puede_editar_alumno(self):
        """Alumno → GET /usuarios/alumnos/<pk>/editar/ recibe HTTP 403."""
        self.client.login(username='alumno_normal', password='pass1234')
        respuesta = self.client.get(reverse('alumno_editar', args=[self.alumno_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder editar registros de otros alumnos',
        )

    def test_instructor_no_puede_editar_alumno(self):
        """Instructor → GET /usuarios/alumnos/<pk>/editar/ recibe HTTP 403."""
        self.client.login(username='instructor_normal', password='pass1234')
        respuesta = self.client.get(reverse('alumno_editar', args=[self.alumno_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder editar registros de alumnos',
        )

    # -- Eliminar alumno ------------------------------------------------------

    def test_admin_puede_eliminar_alumno(self):
        """Admin → GET /usuarios/alumnos/<pk>/eliminar/ recibe HTTP 200."""
        self.client.login(username='admin_alumnos', password='pass1234')
        respuesta = self.client.get(reverse('alumno_eliminar', args=[self.alumno_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder a la confirmación de eliminación de alumnos',
        )

    def test_alumno_no_puede_eliminar_alumno(self):
        """Alumno → GET /usuarios/alumnos/<pk>/eliminar/ recibe HTTP 403."""
        self.client.login(username='alumno_normal', password='pass1234')
        respuesta = self.client.get(reverse('alumno_eliminar', args=[self.alumno_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder eliminar registros de otros alumnos',
        )

    def test_instructor_no_puede_eliminar_alumno(self):
        """Instructor → GET /usuarios/alumnos/<pk>/eliminar/ recibe HTTP 403."""
        self.client.login(username='instructor_normal', password='pass1234')
        respuesta = self.client.get(reverse('alumno_eliminar', args=[self.alumno_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder eliminar registros de alumnos',
        )


# ---------------------------------------------------------------------------
# Test 5b: CRUD de Instructores — solo el admin tiene permiso
# ---------------------------------------------------------------------------

class PermisosInstructorCRUDTest(TestCase):
    """
    RF: Un alumno o instructor normal recibe HTTP 403 al intentar crear,
    editar o eliminar instructores. Solo el admin puede realizar estas acciones.
    """

    def setUp(self):
        self.user_admin = crear_usuario_con_perfil('admin_inst', 'pass1234', 'admin')
        self.user_alumno = crear_usuario_con_perfil('alumno_inst', 'pass1234', 'alumno')
        self.user_instructor = crear_usuario_con_perfil('instructor_inst', 'pass1234', 'instructor')

        # Instructor existente para editar/eliminar
        self.instructor_objetivo = crear_instructor_de_prueba(1)

    # -- Crear instructor -----------------------------------------------------

    def test_admin_puede_crear_instructor(self):
        """Admin → GET /usuarios/instructores/nuevo/ recibe HTTP 200."""
        self.client.login(username='admin_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_crear'))

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder al formulario de creación de instructores',
        )

    def test_alumno_no_puede_crear_instructor(self):
        """Alumno → GET /usuarios/instructores/nuevo/ recibe HTTP 403."""
        self.client.login(username='alumno_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_crear'))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder crear instructores',
        )

    def test_instructor_no_puede_crear_instructor(self):
        """Instructor → GET /usuarios/instructores/nuevo/ recibe HTTP 403."""
        self.client.login(username='instructor_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_crear'))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder crear otros instructores',
        )

    # -- Editar instructor ----------------------------------------------------

    def test_admin_puede_editar_instructor(self):
        """Admin → GET /usuarios/instructores/<pk>/editar/ recibe HTTP 200."""
        self.client.login(username='admin_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_editar', args=[self.instructor_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder editar instructores',
        )

    def test_alumno_no_puede_editar_instructor(self):
        """Alumno → GET /usuarios/instructores/<pk>/editar/ recibe HTTP 403."""
        self.client.login(username='alumno_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_editar', args=[self.instructor_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder editar instructores',
        )

    def test_instructor_no_puede_editar_instructor(self):
        """Instructor → GET /usuarios/instructores/<pk>/editar/ recibe HTTP 403."""
        self.client.login(username='instructor_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_editar', args=[self.instructor_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder editar registros de otros instructores',
        )

    # -- Eliminar instructor --------------------------------------------------

    def test_admin_puede_eliminar_instructor(self):
        """Admin → GET /usuarios/instructores/<pk>/eliminar/ recibe HTTP 200."""
        self.client.login(username='admin_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_eliminar', args=[self.instructor_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 200,
            'El admin debe poder acceder a la confirmación de eliminación de instructores',
        )

    def test_alumno_no_puede_eliminar_instructor(self):
        """Alumno → GET /usuarios/instructores/<pk>/eliminar/ recibe HTTP 403."""
        self.client.login(username='alumno_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_eliminar', args=[self.instructor_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un alumno NO debe poder eliminar instructores',
        )

    def test_instructor_no_puede_eliminar_instructor(self):
        """Instructor → GET /usuarios/instructores/<pk>/eliminar/ recibe HTTP 403."""
        self.client.login(username='instructor_inst', password='pass1234')
        respuesta = self.client.get(reverse('instructor_eliminar', args=[self.instructor_objetivo.pk]))

        self.assertEqual(
            respuesta.status_code, 403,
            'Un instructor NO debe poder eliminar a otros instructores',
        )


# ---------------------------------------------------------------------------
# Test 6: Cierre de sesión — logout destruye la sesión activa
# ---------------------------------------------------------------------------

class LogoutDestruyeSesionTest(TestCase):
    """
    Pruebas relacionadas con el cierre de sesión.

    Se comprueba que al ejecutar logout la sesión del usuario se elimina
    correctamente y que posteriormente ya no puede acceder a vistas
    protegidas sin volver a autenticarse.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario_sesion', password='pass1234'
        )

    def test_logout_destruye_sesion(self):
        """
        Tras llamar a /usuarios/logout/:
          - La respuesta debe ser HTTP 302.
          - La clave '_auth_user_id' ya no debe existir en la sesión.
        """
        # 1. Autenticar al usuario
        login_exitoso = self.client.login(username='usuario_sesion', password='pass1234')
        self.assertTrue(login_exitoso, 'El login debería ser exitoso antes del logout')

        # 2. Confirmar que la sesión está activa (usuario autenticado)
        self.assertIn(
            '_auth_user_id',
            self.client.session,
            'La sesión debe contener el ID del usuario autenticado',
        )

        # 3. Llamar a la vista de logout
        respuesta = self.client.get(reverse('logout'))

        # 4a. Verificar que redirige (HTTP 302)
        self.assertEqual(
            respuesta.status_code, 302,
            'El logout debe redirigir tras cerrar la sesión',
        )

        # 4b. Verificar que la sesión fue destruida
        self.assertNotIn(
            '_auth_user_id',
            self.client.session,
            'Tras el logout, la sesión no debe contener el ID del usuario',
        )

    def test_usuario_no_puede_acceder_a_vista_protegida_tras_logout(self):
        """
        Verificación adicional: después del logout, intentar acceder a una
        vista protegida redirige nuevamente al login (confirma que la sesión
        fue invalidada completamente).
        """
        # Autenticar
        self.client.login(username='usuario_sesion', password='pass1234')

        # Cerrar sesión
        self.client.get(reverse('logout'))

        # Intentar acceder a vista que requiere login
        url_protegida = reverse('mis_inscripciones')
        respuesta = self.client.get(url_protegida)

        self.assertEqual(
            respuesta.status_code, 302,
            'Tras el logout, acceder a vista protegida debe redirigir al login',
        )
        self.assertIn(
            '/usuarios/login/',
            respuesta['Location'],
            'La redirección debe apuntar al login',
        )
