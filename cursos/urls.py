from django.urls import path
from . import views

urlpatterns = [
    path('', views.CursoListView.as_view(), name='curso_lista'),
    path('mis-cursos/', views.CursoInstructorListView.as_view(), name='curso_mis_cursos'),
    path('<int:pk>/', views.CursoDetailView.as_view(), name='curso_detalle'),
    path('nuevo/', views.CursoCreateView.as_view(), name='curso_crear'),
    path('<int:pk>/editar/', views.CursoUpdateView.as_view(), name='curso_editar'),
    path('<int:pk>/eliminar/', views.CursoDeleteView.as_view(), name='curso_eliminar'),
]
