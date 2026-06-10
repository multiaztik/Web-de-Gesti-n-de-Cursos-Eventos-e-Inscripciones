from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .forms import RegistroUsuarioForm, AlumnoForm, InstructorForm, InstructorCreateForm
from .models import Alumno, Instructor, PerfilUsuario


def registro(request):
    """RF01: Registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}! Tu cuenta fue creada exitosamente.')
            return redirect('inicio')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def iniciar_sesion(request):
    """RF02: Inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'inicio'))
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'usuarios/login.html')


def cerrar_sesion(request):
    """RF02: Cierre de sesión."""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
def perfil(request):
    """Vista de perfil del usuario autenticado."""
    try:
        perfil_obj = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        perfil_obj = None

    alumno = None
    instructor = None
    try:
        alumno = request.user.alumno
    except Alumno.DoesNotExist:
        pass
    try:
        instructor = request.user.instructor
    except Instructor.DoesNotExist:
        pass

    return render(request, 'usuarios/perfil.html', {
        'perfil': perfil_obj,
        'alumno': alumno,
        'instructor': instructor,
    })

class AlumnoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    raise_exception = True
    model = Alumno
    template_name = 'usuarios/alumno_lista.html'
    context_object_name = 'alumnos'

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = Alumno.objects.all()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs


class AlumnoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    raise_exception = True
    model = Alumno
    form_class = AlumnoForm
    template_name = 'usuarios/alumno_form.html'
    success_url = reverse_lazy('alumno_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Alumno creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)


class AlumnoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    raise_exception = True
    model = Alumno
    form_class = AlumnoForm
    template_name = 'usuarios/alumno_form.html'
    success_url = reverse_lazy('alumno_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Alumno actualizado exitosamente.')
        return super().form_valid(form)


class AlumnoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    raise_exception = True
    model = Alumno
    template_name = 'usuarios/alumno_confirmar_eliminar.html'
    success_url = reverse_lazy('alumno_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Alumno eliminado.')
        return super().form_valid(form)

class InstructorListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    raise_exception = True
    model = Instructor
    template_name = 'usuarios/instructor_lista.html'
    context_object_name = 'instructores'

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff


class InstructorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    raise_exception = True
    model = Instructor
    form_class = InstructorCreateForm
    template_name = 'usuarios/instructor_form.html'
    success_url = reverse_lazy('instructor_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Instructor "{form.instance.nombre}" creado con usuario "{form.cleaned_data["username"]}".'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)


class InstructorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    raise_exception = True
    model = Instructor
    form_class = InstructorForm
    template_name = 'usuarios/instructor_form.html'
    success_url = reverse_lazy('instructor_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Instructor actualizado exitosamente.')
        return super().form_valid(form)


class InstructorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    raise_exception = True
    model = Instructor
    template_name = 'usuarios/instructor_confirmar_eliminar.html'
    success_url = reverse_lazy('instructor_lista')

    def test_func(self):
        try:
            return self.request.user.perfil.es_admin()
        except PerfilUsuario.DoesNotExist:
            return self.request.user.is_staff

    def form_valid(self, form):
        nombre = self.object.nombre
        usuario = self.object.usuario
        if usuario:
            usuario.delete()
        else:
            self.object.delete()
        messages.success(self.request, f'Instructor "{nombre}" eliminado.')
        return redirect(self.success_url)
