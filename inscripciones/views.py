from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from cursos.models import Curso
from usuarios.models import Alumno, PerfilUsuario
from .models import Inscripcion
from .forms import EvidenciaForm


@login_required
def inscribirse(request, pk):
    """RF07, RF08, RF09, RF15: Inscribir alumno a un curso."""
    curso = get_object_or_404(Curso, pk=pk)

    # Obtener el alumno vinculado al usuario
    try:
        alumno = request.user.alumno
    except Alumno.DoesNotExist:
        messages.error(request, 'Tu cuenta no tiene un perfil de alumno. Contacta al administrador.')
        return redirect('curso_detalle', pk=pk)

    # Regla 3: curso cancelado no acepta inscripciones
    if curso.estado == 'cancelado':
        messages.error(request, 'Este curso está cancelado y no acepta inscripciones.')
        return redirect('curso_detalle', pk=pk)

    if curso.estado == 'cerrado':
        messages.error(request, 'Este curso está cerrado.')
        return redirect('curso_detalle', pk=pk)

    # RF09: evitar duplicados
    if Inscripcion.objects.filter(alumno=alumno, curso=curso).exists():
        messages.warning(request, 'Ya estás inscrito en este curso.')
        return redirect('curso_detalle', pk=pk)

    # RF08: validar cupo
    if not curso.tiene_cupo():
        messages.error(request, 'Lo sentimos, el curso ha alcanzado su cupo máximo.')
        return redirect('curso_detalle', pk=pk)

    Inscripcion.objects.create(alumno=alumno, curso=curso)
    messages.success(request, f'Te has inscrito exitosamente en "{curso.nombre}".')
    return redirect('mis_inscripciones')


@login_required
def mis_inscripciones(request):
    """Lista de cursos en los que el alumno está inscrito."""
    try:
        alumno = request.user.alumno
        inscripciones = Inscripcion.objects.filter(alumno=alumno).select_related('curso', 'curso__instructor')
    except Alumno.DoesNotExist:
        inscripciones = []
        messages.info(request, 'No tienes un perfil de alumno asociado.')
    return render(request, 'inscripciones/mis_inscripciones.html', {'inscripciones': inscripciones})


@login_required
def subir_evidencia(request, pk):
    """RF10: Subir evidencia a una inscripción."""
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    # Solo el alumno dueño puede subir evidencia
    try:
        if inscripcion.alumno != request.user.alumno:
            messages.error(request, 'No tienes permiso para modificar esta inscripción.')
            return redirect('mis_inscripciones')
    except Alumno.DoesNotExist:
        messages.error(request, 'No tienes un perfil de alumno.')
        return redirect('inicio')

    if request.method == 'POST':
        form = EvidenciaForm(request.POST, request.FILES, instance=inscripcion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evidencia subida exitosamente.')
            return redirect('mis_inscripciones')
        else:
            messages.error(request, 'Error al subir el archivo. Verifica el formato y tamaño.')
    else:
        form = EvidenciaForm(instance=inscripcion)
    return render(request, 'inscripciones/subir_evidencia.html', {'form': form, 'inscripcion': inscripcion})


@login_required
def alumnos_inscritos(request, pk):
    """RF11: Ver alumnos inscritos en un curso (admin o instructor)."""
    curso = get_object_or_404(Curso, pk=pk)

    # Solo admin o el instructor del curso
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
    except PerfilUsuario.DoesNotExist:
        es_admin = request.user.is_staff

    if not (es_admin or es_instructor_del_curso):
        messages.error(request, 'No tienes permiso para ver esta información.')
        return redirect('curso_lista')

    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('alumno')
    return render(request, 'inscripciones/alumnos_inscritos.html', {
        'curso': curso,
        'inscripciones': inscripciones,
    })
