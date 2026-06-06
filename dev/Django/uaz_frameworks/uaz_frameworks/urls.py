from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    lista_cursos,
    crear_curso, editar_curso, eliminar_curso,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('cursos/crear/', crear_curso, name='crear_curso'),
    path('cursos/editar/<int:id>/', editar_curso, name='editar_curso'),
    path('cursos/eliminar/<int:id>/', eliminar_curso, name='eliminar_curso'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
