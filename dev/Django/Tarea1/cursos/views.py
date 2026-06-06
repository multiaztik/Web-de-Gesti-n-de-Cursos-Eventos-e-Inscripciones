from django.shortcuts import render
from .models import Curso


def lista_cursos(request):
    """Vista que consulta y muestra todos los cursos registrados."""
    cursos = Curso.objects.all()
    return render(request, 'cursos/lista_cursos.html', {'cursos': cursos})
