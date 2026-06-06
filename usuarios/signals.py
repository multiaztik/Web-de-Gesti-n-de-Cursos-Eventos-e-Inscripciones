from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    """Crea PerfilUsuario solo para superusuarios creados desde el admin/CLI.
    Los usuarios del formulario de registro ya crean su perfil con el tipo correcto."""
    if created and instance.is_superuser:
        PerfilUsuario.objects.get_or_create(usuario=instance, defaults={'tipo': 'admin'})
