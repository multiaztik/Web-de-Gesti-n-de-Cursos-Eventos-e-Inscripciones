from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from cursos.api_views import CursoViewSet, AlumnoViewSet, InscripcionViewSet, InstructorViewSet
from cursos.views import inicio

router = DefaultRouter()
router.register(r'cursos', CursoViewSet)
router.register(r'alumnos', AlumnoViewSet)
router.register(r'inscripciones', InscripcionViewSet)
router.register(r'instructores', InstructorViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='inicio'),
    path('cursos/', include('cursos.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('inscripciones/', include('inscripciones.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
