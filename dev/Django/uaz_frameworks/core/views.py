from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Miembro, Curso
from .forms import MiembroForm, CursoForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from rest_framework import viewsets
from .serializers import MiembroSerializer

class MiembroViewSet(viewsets.ModelViewSet):
    queryset = Miembro.objects.all()
    serializer_class = MiembroSerializer


def home(request):
    return render(request, 'core/home.html')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("lista_miembros")

    else:
        form = AuthenticationForm()

    return render(request, "core/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

def lista_miembros(request):
    miembros = Miembro.objects.all()
    return render(request, 'core/lista_miembros.html', {'miembros': miembros})

def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'core/lista_cursos.html', {'cursos': cursos})


class MiembroCreateView(LoginRequiredMixin, CreateView):
    model = Miembro
    form_class = MiembroForm
    template_name = 'core/crear_miembro.html'
    success_url = reverse_lazy('lista_miembros')


class MiembroListView(LoginRequiredMixin, ListView):
    model = Miembro
    template_name = 'core/lista_miembros.html'
    context_object_name = 'miembros'


class MiembroUpdateView(LoginRequiredMixin, UpdateView):
    model = Miembro
    form_class = MiembroForm
    template_name = 'core/editar_miembro.html'
    success_url = reverse_lazy('lista_miembros')


class MiembroDeleteView(LoginRequiredMixin, DeleteView):
    model = Miembro
    template_name = 'core/confirmar_eliminar.html'
    success_url = reverse_lazy('lista_miembros')


@login_required
def crear_miembro(request):
    if request.method == 'POST':
        form = MiembroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Miembro creado exitosamente.')
            return redirect('lista_miembros')
    else:
        form = MiembroForm()
    return render(request, 'core/crear_miembro.html', {'form': form})

@login_required
def editar_miembro(request, id):
    miembro = get_object_or_404(Miembro, id=id)
    if request.method == 'POST':
        form = MiembroForm(request.POST, instance=miembro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Miembro actualizado exitosamente.')
            return redirect('lista_miembros')
    else:
        form = MiembroForm(instance=miembro)
    return render(request, 'core/editar_miembro.html', {'form': form, 'miembro': miembro})

@login_required
def eliminar_miembro(request, id):
    miembro = get_object_or_404(Miembro, id=id)
    miembro.delete()
    messages.success(request, 'Miembro eliminado exitosamente.')
    return redirect('lista_miembros')

@login_required
def crear_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso creado exitosamente.')
            return redirect('lista_cursos')
    else:
        form = CursoForm()
    return render(request, 'core/crear_curso.html', {'form': form})

@login_required
def editar_curso(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso actualizado exitosamente.')
            return redirect('lista_cursos')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'core/editar_curso.html', {'form': form, 'curso': curso})

@login_required
def eliminar_curso(request, id):
    curso = get_object_or_404(Curso, id=id)
    curso.delete()
    messages.success(request, 'Curso eliminado exitosamente.')
    return redirect('lista_cursos')
