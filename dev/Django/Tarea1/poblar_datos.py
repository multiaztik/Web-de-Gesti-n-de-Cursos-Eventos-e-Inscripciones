import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cursos.settings')
django.setup()

from cursos.models import Curso
from datetime import date

cursos_data = [
    {
        'nombre': 'Desarrollo Web con Django',
        'descripcion': 'Aprende a crear aplicaciones web con el framework Django de Python.',
        'instructor': 'Ing. Carlos López',
        'duracion_horas': 40,
        'fecha_inicio': date(2026, 3, 1),
        'fecha_fin': date(2026, 4, 30),
        'activo': True,
    },
    {
        'nombre': 'Bases de Datos con MySQL',
        'descripcion': 'Curso completo de diseño y administración de bases de datos MySQL.',
        'instructor': 'Lic. María García',
        'duracion_horas': 30,
        'fecha_inicio': date(2026, 3, 15),
        'fecha_fin': date(2026, 5, 15),
        'activo': True,
    },
    {
        'nombre': 'Programación en Python',
        'descripcion': 'Fundamentos y programación avanzada en Python.',
        'instructor': 'Dr. Roberto Hernández',
        'duracion_horas': 50,
        'fecha_inicio': date(2026, 2, 1),
        'fecha_fin': date(2026, 4, 1),
        'activo': True,
    },
    {
        'nombre': 'Inteligencia Artificial',
        'descripcion': 'Introducción a la IA y machine learning con Python.',
        'instructor': 'Dra. Ana Martínez',
        'duracion_horas': 60,
        'fecha_inicio': date(2026, 4, 1),
        'fecha_fin': date(2026, 6, 30),
        'activo': False,
    },
    {
        'nombre': 'Redes y Seguridad Informática',
        'descripcion': 'Conceptos de redes, protocolos y ciberseguridad.',
        'instructor': 'Ing. Pedro Sánchez',
        'duracion_horas': 35,
        'fecha_inicio': date(2026, 3, 10),
        'fecha_fin': date(2026, 5, 10),
        'activo': True,
    },
]

for data in cursos_data:
    curso, created = Curso.objects.get_or_create(nombre=data['nombre'], defaults=data)
    if created:
        print(f'[CREADO] {curso.nombre}')
    else:
        print(f'[YA EXISTE] {curso.nombre}')

print(f'\nTotal de cursos: {Curso.objects.count()}')
