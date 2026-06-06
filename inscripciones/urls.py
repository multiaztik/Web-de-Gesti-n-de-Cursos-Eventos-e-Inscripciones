from django.urls import path
from . import views

urlpatterns = [
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('inscribirse/<int:pk>/', views.inscribirse, name='inscribirse'),
    path('<int:pk>/evidencia/', views.subir_evidencia, name='subir_evidencia'),
    path('curso/<int:pk>/inscritos/', views.alumnos_inscritos, name='alumnos_inscritos'),
]
