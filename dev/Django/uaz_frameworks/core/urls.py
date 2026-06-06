from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MiembroListView,
    MiembroCreateView,
    MiembroUpdateView,
    MiembroDeleteView,
    MiembroViewSet,
    home,
    login_view,
    logout_view,
)

router = DefaultRouter()
router.register(r'api/miembros', MiembroViewSet, basename='miembro')

urlpatterns = [
    path('', home, name='home'),
    path('miembros/', MiembroListView.as_view(), name='lista_miembros'),
    path('miembros/crear/', MiembroCreateView.as_view(), name='crear_miembro'),
    path('miembros/editar/<int:pk>/', MiembroUpdateView.as_view(), name='editar_miembro'),
    path('miembros/eliminar/<int:pk>/', MiembroDeleteView.as_view(), name='eliminar_miembro'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]
