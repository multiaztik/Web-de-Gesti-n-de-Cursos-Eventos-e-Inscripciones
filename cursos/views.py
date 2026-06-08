from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .models import Curso
from .forms import CursoForm, BusquedaCursoForm
from usuarios.models import PerfilUsuario


def inicio(request):
    """Página de inicio con cursos activos destacados."""
    cursos_activos = Curso.objects.filter(estado='activo')[:6]
    return render(request, 'inicio.html', {'cursos_activos': cursos_activos})


class CursoListView(ListView):
    """RF06: Lista de cursos con búsqueda y filtrado (RF12)."""
    model = Curso
    template_name = 'cursos/curso_lista.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        qs = Curso.objects.select_related('instructor')
        form = BusquedaCursoForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            estado = form.cleaned_data.get('estado')
            instructor = form.cleaned_data.get('instructor')
            if q:
                qs = qs.filter(nombre__icontains=q)
            if estado:
                qs = qs.filter(estado=estado)
            if instructor:
                qs = qs.filter(instructor__nombre__icontains=instructor)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_busqueda'] = BusquedaCursoForm(self.request.GET)
        return ctx


class CursoDetailView(DetailView):
    """RF06: Detalle de un curso."""
    model = Curso
    template_name = 'cursos/curso_detalle.html'
    context_object_name = 'curso'

    def get_context_data(self, **kwargs):
        from django.core.exceptions import ObjectDoesNotExist
        ctx = super().get_context_data(**kwargs)
        curso = self.get_object()
        alumno = None
        ya_inscrito = False
        if self.request.user.is_authenticated:
            try:
                alumno = self.request.user.alumno
                ya_inscrito = curso.inscripciones.filter(alumno=alumno, estado='activa').exists()
            except (AttributeError, ObjectDoesNotExist):
                pass
        ctx['ya_inscrito'] = ya_inscrito
        ctx['alumno'] = alumno
        return ctx


class CursoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """RF05: Crear curso (solo admin)."""
    raise_exception = True
    model = Curso
    form_class = CursoForm
    template_name = 'cursos/curso_form.html'
    success_url = reverse_lazy('curso_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f'Curso "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)


class CursoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """RF05: Editar curso (solo admin)."""
    raise_exception = True
    model = Curso
    form_class = CursoForm
    template_name = 'cursos/curso_form.html'
    success_url = reverse_lazy('curso_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f'Curso "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)


class CursoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """RF05: Eliminar curso (solo admin — RF15, Regla 7)."""
    raise_exception = True
    model = Curso
    template_name = 'cursos/curso_confirmar_eliminar.html'
    success_url = reverse_lazy('curso_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Curso eliminado.')
        return super().form_valid(form)
