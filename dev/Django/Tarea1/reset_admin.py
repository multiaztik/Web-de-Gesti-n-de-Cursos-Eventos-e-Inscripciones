import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cursos.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('Contrasena actualizada correctamente para el usuario "admin"')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@sistema.com', 'admin123')
    print('Superusuario "admin" creado correctamente')

print(f'Usuario: admin')
print(f'Contrasena: admin123')
