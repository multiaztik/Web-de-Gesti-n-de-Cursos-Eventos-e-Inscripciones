import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

# 1. Importación de tus modelos exactos
from cursos.models import Curso
from inscripciones.models import Inscripcion
from usuarios.models import Alumno, Instructor

# 2. Importación de los formularios con sus nombres reales
from cursos.forms import CursoForm
from inscripciones.forms import EvidenciaForm
from usuarios.forms import RegistroUsuarioForm, AlumnoForm, InstructorForm


class ProyectoFinalUnitTests(TestCase):

    def setUp(self):
        """PREPARACIÓN (Arrange): Escenario inicial idéntico a la estructura real."""
        # Creación de usuarios base en Django
        self.user_instructor = User.objects.create_user(username='instructor1', email='inst@uaz.edu.mx', password='123')
        self.user_alumno1 = User.objects.create_user(username='alumno1', email='blanca@email.com', password='123')
        self.user_alumno2 = User.objects.create_user(username='alumno2', email='efrain@email.com', password='123')

        # Perfiles de Alumnos e Instructores (Usando los campos exactos de tus modelos)
        self.instructor = Instructor.objects.create(
            usuario=self.user_instructor, 
            nombre="Dr. Alejandro Isais",
            correo="alejandroisais@uaz.edu.mx", 
            especialidad="Frameworks"
        )
        self.alumno1 = Alumno.objects.create(
            usuario=self.user_alumno1, 
            nombre="Blanca Díaz",
            correo="blanca@email.com", 
            matricula="123456"
        )
        self.alumno2 = Alumno.objects.create(
            usuario=self.user_alumno2, 
            nombre="Efraín",
            correo="efrain@email.com", 
            matricula="654321"
        )

        # Curso base para pruebas lógicas
        self.curso = Curso.objects.create(
            nombre="Desarrollo Web con Django",
            descripcion="Pruebas unitarias intensivas",
            fecha_inicio=timezone.now().date(),
            fecha_termino=timezone.now().date() + datetime.timedelta(days=10),
            cupo_maximo=2,
            instructor=self.instructor,
            estado="activo"
        )

    # 1. LÓGICA DEL MODELO CURSO
    def test_logica_cupo_y_disponibilidad_curso(self):
        """Verifica que cupo_disponible() reste correctamente y tiene_cupo() cambie a False."""
        self.assertEqual(self.curso.cupo_disponible(), 2)
        self.assertTrue(self.curso.tiene_cupo())

        Inscripcion.objects.create(alumno=self.alumno1, curso=self.curso, estado='activa')
        self.assertEqual(
            self.curso.cupo_disponible(), 1,
            "ERROR: El cupo disponible no se restó tras inscribir un alumno (inconsistencia de estado de inscripción)."
        )
        self.assertTrue(self.curso.tiene_cupo())

        Inscripcion.objects.create(alumno=self.alumno2, curso=self.curso, estado='activa')
        self.assertEqual(
            self.curso.cupo_disponible(), 0,
            "ERROR: El cupo disponible debería ser 0 al completarse el cupo máximo."
        )
        self.assertFalse(self.curso.tiene_cupo())

    # 2. RESTRICCIÓN DE INSCRIPCIÓN ÚNICA (BASE DE DATOS)
    def test_restriccion_fisica_inscripcion_unica(self):
        """La base de datos debe lanzar IntegrityError si se intenta duplicar alumno y curso."""
        Inscripcion.objects.create(alumno=self.alumno1, curso=self.curso, estado='activa')
        
        with self.assertRaises(IntegrityError):
            Inscripcion.objects.create(alumno=self.alumno1, curso=self.curso, estado='activa')

    # 2.5 VALIDACIÓN DE NOMBRE MÍNIMO (CURSO)
    def test_formulario_curso_rechaza_nombre_corto(self):
        """El CursoForm debe rechazar nombres con menos de tres caracteres."""
        form_data = {
            'nombre': 'Ab',  # Inválido: Menos de 3 caracteres
            'descripcion': 'Test de validación de nombre',
            'fecha_inicio': timezone.now().date(),
            'fecha_termino': timezone.now().date() + datetime.timedelta(days=5),
            'cupo_maximo': 10,
            'estado': 'activo',
            'instructor': self.instructor.id
        }
        form = CursoForm(data=form_data)
        self.assertFalse(
            form.is_valid(),
            "ERROR: El formulario no debe ser válido si el nombre del curso tiene menos de 3 caracteres."
        )
        self.assertIn('nombre', form.errors)

    # 3. VALIDACIÓN DEL CUPO MÍNIMO (CURSO)
    def test_formulario_curso_rechaza_cupo_invalido(self):
        """El CursoForm debe rechazar cupos máximos menores o iguales a cero."""
        form_data = {
            'nombre': 'Curso Test', 
            'descripcion': 'Test de validación',
            'fecha_inicio': timezone.now().date(),
            'fecha_termino': timezone.now().date() + datetime.timedelta(days=5),
            'cupo_maximo': 0,  # Inválido: Regla clean_cupo_maximo
            'estado': 'activo', 
            'instructor': self.instructor.id
        }
        form = CursoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cupo_maximo', form.errors)

    # 4. VALIDACIÓN DE FECHAS DEL CURSO
    def test_formulario_curso_rechaza_fecha_termino_anterior(self):
        """El clean() de CursoForm debe invalidar si la fecha_termino es menor a fecha_inicio."""
        form_data = {
            'nombre': 'Curso Fechas Incorrectas',
            'descripcion': 'Probando las fechas',
            'fecha_inicio': timezone.now().date(),
            'fecha_termino': timezone.now().date() - datetime.timedelta(days=2),  # Anterior a inicio
            'cupo_maximo': 15,
            'estado': 'activo',
            'instructor': self.instructor.id
        }
        form = CursoForm(data=form_data)
        self.assertFalse(form.is_valid())

    # 5. VALIDACIÓN DE REGISTRO DE USUARIOS (CORREO DUPLICADO)
    def test_registro_usuario_impide_correo_duplicado(self):
        """El RegistroUsuarioForm debe impedir crear cuentas con correos ya existentes."""
        form_data = {
            'username': 'nuevo_usuario_test',
            'first_name': 'Brenda',
            'last_name': 'Diaz',
            'email': 'blanca@email.com',  # Correo ya usado en el setUp()
            'password1': 'UAZframeworks2026',
            'password2': 'UAZframeworks2026'
        }
        form = RegistroUsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # 6. VALIDACIÓN DE ARCHIVO DE EVIDENCIA
    def test_validacion_archivo_evidencia_tamano_y_extension(self):
        """Prueba que el validador de EvidenciaForm rechace extensiones prohibidas o exceso de peso."""
        # Caso A: Extensión prohibida (.exe)
        file_exe = SimpleUploadedFile("script.exe", b"bytes_fake", content_type="application/x-msdownload")
        form_exe = EvidenciaForm(files={'evidencia': file_exe})
        self.assertFalse(form_exe.is_valid())

        # Caso B: Extensión válida (.pdf)
        file_pdf = SimpleUploadedFile("comprobante.pdf", b"bytes_pdf", content_type="application/pdf")
        form_pdf = EvidenciaForm(files={'evidencia': file_pdf})
        self.assertTrue(form_pdf.is_valid() or 'evidencia' not in form_pdf.errors)

        # Caso C: Archivo que supera los 10 MB
        file_grande = SimpleUploadedFile("archivo_pesado.pdf", b"datos", content_type="application/pdf")
        file_grande.size = 12 * 1024 * 1024  # 12 Megabytes
        form_grande = EvidenciaForm(files={'evidencia': file_grande})
        self.assertFalse(form_grande.is_valid())

    # 7. VALIDACIONES DE ALUMNO E INSTRUCTOR (REGLAS DE NOMBRE Y CORREO)
    def test_perfiles_requieren_nombre_valido_y_correo_unico(self):
        """AlumnoForm e InstructorForm bloquean nombres cortos (< 3 caracteres) y correos duplicados."""
        # Alumno con nombre de menos de 3 caracteres
        data_alumno = {'nombre': 'Bl', 'correo': 'correo_nuevo@email.com', 'matricula': 'AL0099'}
        form_al = AlumnoForm(data=data_alumno)
        self.assertFalse(form_al.is_valid())
        self.assertIn('nombre', form_al.errors)

        # Instructor con correo duplicado
        data_instructor = {'nombre': 'Ing. Nuevo', 'correo': 'alejandroisais@uaz.edu.mx', 'especialidad': 'AI'}
        form_inst = InstructorForm(data=data_instructor)
        self.assertFalse(form_inst.is_valid())
        self.assertIn('correo', form_inst.errors)