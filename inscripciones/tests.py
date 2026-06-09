"""
Pruebas de integración: Seguridad y control de acceso — app inscripciones
==========================================================================

Cubre los siguientes casos del checklist:
  ✔ Protección de vistas básicas (anónimos → redirigen al login)
  ✔ Protección de evidencias (alumno no puede ver/modificar evidencia ajena)
  ✔ Acceso a la lista de alumnos inscritos (solo admin o instructor del curso)
"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cursos.models import Curso
from inscripciones.models import Inscripcion
from usuarios.models import Alumno, Instructor, PerfilUsuario


# ---------------------------------------------------------------------------
# Fixtures reutilizables
# ---------------------------------------------------------------------------

def crear_usuario_con_perfil(username, password, tipo):
    """Crea un User + PerfilUsuario con el rol indicado ('alumno'|'instructor'|'admin')."""
    user = User.objects.create_user(username=username, password=password)
    PerfilUsuario.objects.create(usuario=user, tipo=tipo)
    return user


def crear_alumno_para_usuario(user, matricula, correo):
    """Crea un Alumno vinculado al User dado."""
    return Alumno.objects.create(
        usuario=user,
        nombre=user.get_full_name() or user.username,
        correo=correo,
        matricula=matricula,
    )


def crear_curso_base(instructor=None):
    """Crea un Curso activo para usar en las pruebas."""
    return Curso.objects.create(
        nombre='Curso de Prueba',
        descripcion='Descripción de prueba',
        fecha_inicio=datetime.date.today(),
        fecha_termino=datetime.date.today() + datetime.timedelta(days=30),
        cupo_maximo=20,
        instructor=instructor,
        estado='activo',
    )


# ---------------------------------------------------------------------------
# Test 1: Protección de vistas básicas (usuarios anónimos)
# ---------------------------------------------------------------------------

class ProteccionVistasAnonimasTest(TestCase):
    """
    Pruebas de acceso para usuarios sin iniciar sesión.

    Se verifica que las vistas protegidas redirijan al login cuando el
    usuario intenta acceder sin estar autenticado.
    """

    def setUp(self):
        # Creamos un curso y una inscripción para tener PKs válidos
        # (aunque el usuario anónimo no llegará a ver su contenido)
        user_alumno = crear_usuario_con_perfil('alumno_anon', 'pass1234', 'alumno')
        alumno = crear_alumno_para_usuario(user_alumno, 'A001', 'anon@test.com')
        self.curso = crear_curso_base()
        self.inscripcion = Inscripcion.objects.create(alumno=alumno, curso=self.curso)

    def test_inscribirse_anonimo_redirige_login(self):
        """
        GET /inscripciones/inscribirse/<pk>/ sin sesión
        → HTTP 302 hacia /usuarios/login/?next=...
        """
        url = reverse('inscribirse', args=[self.curso.pk])
        respuesta = self.client.get(url)

        # Verificamos la redirección al login
        self.assertRedirects(
            respuesta,
            f'/usuarios/login/?next={url}',
            msg_prefix='[inscribirse] Anónimo debería ser redirigido al login',
        )

    def test_mis_inscripciones_anonimo_redirige_login(self):
        """
        GET /inscripciones/mis-inscripciones/ sin sesión
        → HTTP 302 hacia /usuarios/login/?next=...
        """
        url = reverse('mis_inscripciones')
        respuesta = self.client.get(url)

        self.assertRedirects(
            respuesta,
            f'/usuarios/login/?next={url}',
            msg_prefix='[mis_inscripciones] Anónimo debería ser redirigido al login',
        )

    def test_subir_evidencia_anonimo_redirige_login(self):
        """
        GET /inscripciones/<pk>/evidencia/ sin sesión
        → HTTP 302 hacia /usuarios/login/?next=...
        """
        url = reverse('subir_evidencia', args=[self.inscripcion.pk])
        respuesta = self.client.get(url)

        self.assertRedirects(
            respuesta,
            f'/usuarios/login/?next={url}',
            msg_prefix='[subir_evidencia] Anónimo debería ser redirigido al login',
        )


# ---------------------------------------------------------------------------
# Test 2: Protección de evidencias de otros alumnos
# ---------------------------------------------------------------------------

class ProteccionEvidenciaAjenaTest(TestCase):
    """
   Pruebas de protección de evidencias.

    Se comprueba que un alumno solo pueda acceder a las evidencias de sus
    propias inscripciones y no a las de otros usuarios. 
    """

    def setUp(self):
        # Alumno propietario de la inscripción
        self.user_dueno = crear_usuario_con_perfil('dueno', 'pass1234', 'alumno')
        alumno_dueno = crear_alumno_para_usuario(self.user_dueno, 'A002', 'dueno@test.com')

        # Alumno intruso que intentará acceder
        self.user_intruso = crear_usuario_con_perfil('intruso', 'pass1234', 'alumno')
        crear_alumno_para_usuario(self.user_intruso, 'A003', 'intruso@test.com')

        self.curso = crear_curso_base()
        # Inscripción pertenece al dueño
        self.inscripcion_dueno = Inscripcion.objects.create(
            alumno=alumno_dueno, curso=self.curso
        )

    def test_alumno_no_puede_ver_evidencia_ajena(self):
        """
        El alumno 'intruso' hace GET a la URL de evidencia que pertenece a 'dueno'.
        Debe recibir un HTTP 302 hacia 'mis_inscripciones' (sin poder modificar nada).
        """
        self.client.login(username='intruso', password='pass1234')

        url = reverse('subir_evidencia', args=[self.inscripcion_dueno.pk])
        respuesta = self.client.get(url)

        # La vista redirige (no muestra el formulario al intruso)
        self.assertEqual(
            respuesta.status_code, 302,
            'El alumno intruso no debería poder acceder a evidencia ajena',
        )
        self.assertRedirects(respuesta, reverse('mis_inscripciones'))

    def test_dueno_puede_ver_su_propia_evidencia(self):
        """
        El alumno dueño sí puede acceder a su propio formulario de evidencia
        y recibe HTTP 200.
        """
        self.client.login(username='dueno', password='pass1234')

        url = reverse('subir_evidencia', args=[self.inscripcion_dueno.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 200,
            'El dueño de la inscripción debe poder ver su propia evidencia',
        )


# ---------------------------------------------------------------------------
# Test 3: Lista de alumnos inscritos (acceso restringido)
# ---------------------------------------------------------------------------

class AccesoAlumnosInscritosTest(TestCase):
    """
    Pruebas de acceso a la lista de inscritos.

    Se verifica que únicamente el administrador o el instructor asignado
    al curso puedan consultar la lista de alumnos inscritos. 
    """

    def setUp(self):
        # Admin
        self.user_admin = crear_usuario_con_perfil('admin_test', 'pass1234', 'admin')

        # Instructor (vinculado al curso)
        self.user_instructor = crear_usuario_con_perfil('instructor_test', 'pass1234', 'instructor')
        self.instructor_obj = Instructor.objects.create(
            usuario=self.user_instructor,
            nombre='Instructor Test',
            correo='instructor@test.com',
            especialidad='Programación',
        )

        # Alumno común
        self.user_alumno = crear_usuario_con_perfil('alumno_test', 'pass1234', 'alumno')
        crear_alumno_para_usuario(self.user_alumno, 'A004', 'alumno@test.com')

        # Curso asignado al instructor
        self.curso = crear_curso_base(instructor=self.instructor_obj)

    def test_alumno_no_puede_ver_lista_inscritos(self):
        """
        El alumno común intenta acceder a la lista de inscritos.
        Debe recibir HTTP 302 (redirigido a curso_lista).
        """
        self.client.login(username='alumno_test', password='pass1234')
        url = reverse('alumnos_inscritos', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertRedirects(
            respuesta,
            reverse('curso_lista'),
            msg_prefix='[alumnos_inscritos] Alumno común debe ser redirigido',
        )

    def test_admin_puede_ver_lista_inscritos(self):
        """
        El administrador accede a la lista de inscritos.
        Debe recibir HTTP 200.
        """
        self.client.login(username='admin_test', password='pass1234')
        url = reverse('alumnos_inscritos', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 200,
            'El administrador debe poder ver la lista de alumnos inscritos',
        )

    def test_instructor_del_curso_puede_ver_lista_inscritos(self):
        """
        El instructor asignado al curso accede a la lista de inscritos.
        Debe recibir HTTP 200.
        """
        self.client.login(username='instructor_test', password='pass1234')
        url = reverse('alumnos_inscritos', args=[self.curso.pk])
        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code, 200,
            'El instructor del curso debe poder ver la lista de alumnos inscritos',
        )
