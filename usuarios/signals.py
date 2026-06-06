from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    """Crea automáticamente un PerfilUsuario cuando se crea un User."""
    if created and not hasattr(instance, 'perfil'):
        PerfilUsuario.objects.get_or_create(usuario=instance)
