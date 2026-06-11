import os
from datetime import date

import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from cursos.models import Curso
from inscripciones.models import Inscripcion
from usuarios.models import Alumno, Instructor, PerfilUsuario

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_cursos.settings")


@pytest.fixture
def instructor(db):
    return Instructor.objects.create(
        nombre='Dr. Alejandro Isais',
        correo='alejandro@pruebas.com',
        especialidad='Programación Delphi',
        telefono='4921234567',
    )


@pytest.fixture
def alumno_user(db):
    user = User.objects.create_user(username='alumno1', password='clave12345')
    PerfilUsuario.objects.create(usuario=user, tipo='alumno')
    alumno = Alumno.objects.create(
        usuario=user,
        nombre='Juan Pérez',
        correo='juan@pruebas.com',
        matricula='AL0001',
        telefono='1234567890',
    )
    return user, alumno


def crear_curso(instructor, estado='activo', cupo_maximo=20):
    return Curso.objects.create(
        nombre='Desarrollo Web con Django',
        descripcion='Aprende a construir aplicaciones web completas usando Django y Python.',
        fecha_inicio=date(2026, 7, 1),
        fecha_termino=date(2026, 8, 31),
        cupo_maximo=cupo_maximo,
        instructor=instructor,
        estado=estado,
    )


def get_messages_text(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


@pytest.mark.django_db
def test_inscripcion_curso_cancelado(client, instructor, alumno_user):
    """Inscripción en curso cancelado: error en mensajes flash y no crea la inscripción."""
    user, alumno = alumno_user
    curso = crear_curso(instructor, estado='cancelado')

    client.login(username='alumno1', password='clave12345')
    response = client.post(reverse('inscribirse', args=[curso.pk]), follow=True)

    mensajes = get_messages_text(response)
    assert any('cancelado' in m.lower() for m in mensajes)
    assert not Inscripcion.objects.filter(alumno=alumno, curso=curso).exists()


@pytest.mark.django_db
def test_inscripcion_curso_cerrado(client, instructor, alumno_user):
    """Inscripción en curso cerrado: solicitud rechazada y redirigida con mensaje de alerta."""
    user, alumno = alumno_user
    curso = crear_curso(instructor, estado='cerrado')

    client.login(username='alumno1', password='clave12345')
    response = client.post(reverse('inscribirse', args=[curso.pk]))

    assert response.status_code == 302
    assert response.url == reverse('curso_detalle', args=[curso.pk])

    response = client.post(reverse('inscribirse', args=[curso.pk]), follow=True)
    mensajes = get_messages_text(response)
    assert any('cerrado' in m.lower() for m in mensajes)
    assert not Inscripcion.objects.filter(alumno=alumno, curso=curso).exists()


@pytest.mark.django_db
def test_inscripcion_curso_lleno(client, instructor, alumno_user):
    """Inscripción en curso lleno: la vista indica que no hay cupo y no guarda la inscripción."""
    user, alumno = alumno_user
    curso = crear_curso(instructor, estado='activo', cupo_maximo=1)

    # Llenar el cupo con otro alumno ya inscrito
    otro_user = User.objects.create_user(username='alumno2', password='clave12345')
    PerfilUsuario.objects.create(usuario=otro_user, tipo='alumno')
    otro_alumno = Alumno.objects.create(
        usuario=otro_user,
        nombre='Ana López',
        correo='ana@pruebas.com',
        matricula='AL0002',
        telefono='0987654321',
    )
    Inscripcion.objects.create(alumno=otro_alumno, curso=curso, estado='activa')

    assert curso.tiene_cupo() is False

    client.login(username='alumno1', password='clave12345')
    response = client.post(reverse('inscribirse', args=[curso.pk]), follow=True)

    mensajes = get_messages_text(response)
    assert any('cupo' in m.lower() for m in mensajes)
    assert not Inscripcion.objects.filter(alumno=alumno, curso=curso).exists()


@pytest.mark.django_db
def test_carga_evidencia_exitosa(client, instructor, alumno_user):
    """Carga de evidencia exitosa: actualiza la inscripción con la ruta del archivo y muestra éxito."""
    user, alumno = alumno_user
    curso = crear_curso(instructor, estado='activo')
    inscripcion = Inscripcion.objects.create(alumno=alumno, curso=curso, estado='activa')

    archivo = SimpleUploadedFile(
        'comprobante.pdf', b'%PDF-1.4 contenido de prueba', content_type='application/pdf'
    )

    client.login(username='alumno1', password='clave12345')
    response = client.post(
        reverse('subir_evidencia', args=[inscripcion.pk]),
        {'evidencia': archivo},
        follow=True,
    )

    mensajes = get_messages_text(response)
    assert any('exitosamente' in m.lower() for m in mensajes)

    inscripcion.refresh_from_db()
    assert inscripcion.evidencia
    assert 'comprobante' in inscripcion.evidencia.name


@pytest.mark.django_db
def test_busqueda_y_filtrado_cursos(client, instructor):
    """RF12: la búsqueda y filtrado de cursos devuelve solo los cursos que coinciden."""
    Curso.objects.create(
        nombre='Curso de Django',
        descripcion='Curso enfocado en el framework Django.',
        fecha_inicio=date(2026, 7, 1),
        fecha_termino=date(2026, 8, 31),
        cupo_maximo=20,
        instructor=instructor,
        estado='activo',
    )
    Curso.objects.create(
        nombre='Curso de Redes',
        descripcion='Curso de fundamentos de redes.',
        fecha_inicio=date(2026, 7, 1),
        fecha_termino=date(2026, 8, 31),
        cupo_maximo=20,
        instructor=instructor,
        estado='cerrado',
    )

    response = client.get(reverse('curso_lista'), {'q': 'Django'})
    contenido = response.content.decode()
    assert 'Curso de Django' in contenido
    assert 'Curso de Redes' not in contenido

    response = client.get(reverse('curso_lista'), {'estado': 'activo'})
    contenido = response.content.decode()
    assert 'Curso de Django' in contenido
    assert 'Curso de Redes' not in contenido
