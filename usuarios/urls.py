from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),

    # Alumnos
    path('alumnos/', views.AlumnoListView.as_view(), name='alumno_lista'),
    path('alumnos/nuevo/', views.AlumnoCreateView.as_view(), name='alumno_crear'),
    path('alumnos/<int:pk>/editar/', views.AlumnoUpdateView.as_view(), name='alumno_editar'),
    path('alumnos/<int:pk>/eliminar/', views.AlumnoDeleteView.as_view(), name='alumno_eliminar'),

    # Instructores
    path('instructores/', views.InstructorListView.as_view(), name='instructor_lista'),
    path('instructores/nuevo/', views.InstructorCreateView.as_view(), name='instructor_crear'),
    path('instructores/<int:pk>/editar/', views.InstructorUpdateView.as_view(), name='instructor_editar'),
    path('instructores/<int:pk>/eliminar/', views.InstructorDeleteView.as_view(), name='instructor_eliminar'),
]
