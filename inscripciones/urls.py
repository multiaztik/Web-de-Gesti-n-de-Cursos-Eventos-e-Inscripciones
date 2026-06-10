from django.urls import path
from . import views

urlpatterns = [
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('gestion/', views.InscripcionListView.as_view(), name='inscripcion_lista'),
    path('gestion/nueva/', views.InscripcionCreateView.as_view(), name='inscripcion_crear'),
    path('gestion/<int:pk>/editar/', views.InscripcionUpdateView.as_view(), name='inscripcion_editar'),
    path('gestion/<int:pk>/eliminar/', views.InscripcionDeleteView.as_view(), name='inscripcion_eliminar'),
    path('inscribirse/<int:pk>/', views.inscribirse, name='inscribirse'),
    path('<int:pk>/evidencia/', views.subir_evidencia, name='subir_evidencia'),
    path('curso/<int:pk>/inscritos/', views.alumnos_inscritos, name='alumnos_inscritos'),
]
