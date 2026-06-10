from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q

from cursos.models import Curso
from usuarios.models import Alumno, PerfilUsuario
from .models import Inscripcion
from .forms import EvidenciaForm, InscripcionForm


def _es_admin(user):
    try:
        return user.is_staff or user.perfil.es_admin()
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return user.is_staff


@login_required
def inscribirse(request, pk):
    """RF07, RF08, RF09, RF15: Inscribir alumno a un curso."""
    curso = get_object_or_404(Curso, pk=pk)

    try:
        if not request.user.perfil.es_alumno():
            messages.error(request, 'Solo los alumnos pueden inscribirse a cursos.')
            return redirect('curso_detalle', pk=pk)
    except (AttributeError, PerfilUsuario.DoesNotExist):
        messages.error(request, 'Tu cuenta no tiene permiso para inscribirse a cursos.')
        return redirect('curso_detalle', pk=pk)

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
    from django.core.exceptions import ObjectDoesNotExist
    es_admin = False
    es_instructor_del_curso = False
    try:
        if request.user.is_staff or request.user.perfil.es_admin():
            es_admin = True
        if request.user.perfil.es_instructor() and curso.instructor == request.user.instructor:
            es_instructor_del_curso = True
    except (AttributeError, ObjectDoesNotExist):
        if request.user.is_staff:
            es_admin = True

    if not (es_admin or es_instructor_del_curso):
        messages.error(request, 'No tienes permiso para ver esta información.')
        return redirect('curso_lista')

    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('alumno')
    return render(request, 'inscripciones/alumnos_inscritos.html', {
        'curso': curso,
        'inscripciones': inscripciones,
    })

class InscripcionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    raise_exception = True
    model = Inscripcion
    template_name = 'inscripciones/inscripcion_lista.html'
    context_object_name = 'inscripciones'

    def test_func(self):
        return _es_admin(self.request.user)

    def get_queryset(self):
        qs = Inscripcion.objects.select_related('alumno', 'curso', 'curso__instructor')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(alumno__nombre__icontains=q) |
                Q(curso__nombre__icontains=q) |
                Q(alumno__matricula__icontains=q)
            )
        return qs


class InscripcionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    raise_exception = True
    model = Inscripcion
    form_class = InscripcionForm
    template_name = 'inscripciones/inscripcion_form.html'
    success_url = reverse_lazy('inscripcion_lista')

    def test_func(self):
        return _es_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Inscripción creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)


class InscripcionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    raise_exception = True
    model = Inscripcion
    form_class = InscripcionForm
    template_name = 'inscripciones/inscripcion_form.html'
    success_url = reverse_lazy('inscripcion_lista')

    def test_func(self):
        return _es_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Inscripción actualizada exitosamente.')
        return super().form_valid(form)


class InscripcionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    raise_exception = True
    model = Inscripcion
    template_name = 'inscripciones/inscripcion_confirmar_eliminar.html'
    success_url = reverse_lazy('inscripcion_lista')

    def test_func(self):
        return _es_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Inscripción eliminada.')
        return super().form_valid(form)
