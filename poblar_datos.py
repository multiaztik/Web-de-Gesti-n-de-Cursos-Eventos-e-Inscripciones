"""
Script para poblar la base de datos con datos de prueba.
Ejecutar con: python manage.py shell < poblar_datos.py
O directamente: python poblar_datos.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_cursos.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, Alumno, Instructor
from cursos.models import Curso
from inscripciones.models import Inscripcion
from datetime import date

print("Limpiando datos anteriores...")
Inscripcion.objects.all().delete()
Curso.objects.all().delete()
Alumno.objects.all().delete()
Instructor.objects.all().delete()
PerfilUsuario.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# Superusuario admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@scea.mx', 'admin1234')
    admin.first_name = 'Administrador'
    admin.last_name = 'Sistema'
    admin.save()
    PerfilUsuario.objects.filter(usuario=admin).update(tipo='admin')
    print("Superusuario 'admin' creado (contraseña: admin1234)")

# Instructores
inst1 = Instructor.objects.create(
    nombre='Dr. Carlos Ramírez', correo='carlos@scea.mx',
    especialidad='Programación Web', telefono='4921234567'
)
inst2 = Instructor.objects.create(
    nombre='Mtra. Laura Hernández', correo='laura@scea.mx',
    especialidad='Bases de Datos', telefono='4927654321'
)
inst3 = Instructor.objects.create(
    nombre='Ing. Roberto Pérez', correo='roberto@scea.mx',
    especialidad='Redes y Seguridad', telefono='4921112233'
)

# Usuarios instructor
u_inst1 = User.objects.create_user('carlos', 'carlos@scea.mx', 'pass1234',
                                    first_name='Carlos', last_name='Ramírez')
PerfilUsuario.objects.filter(usuario=u_inst1).update(tipo='instructor')
inst1.usuario = u_inst1
inst1.save()

# Cursos
c1 = Curso.objects.create(
    nombre='Desarrollo Web con Django',
    descripcion='Aprende a construir aplicaciones web completas usando Django y Python. '
                'Cubriremos modelos, vistas, templates, formularios y REST APIs.',
    fecha_inicio=date(2026, 7, 1), fecha_termino=date(2026, 8, 31),
    cupo_maximo=20, instructor=inst1, estado='activo'
)
c2 = Curso.objects.create(
    nombre='Bases de Datos Relacionales',
    descripcion='Fundamentos de diseño y administración de bases de datos con SQL y PostgreSQL.',
    fecha_inicio=date(2026, 7, 15), fecha_termino=date(2026, 9, 15),
    cupo_maximo=15, instructor=inst2, estado='activo'
)
c3 = Curso.objects.create(
    nombre='Seguridad Informática',
    descripcion='Conceptos básicos de seguridad en redes, criptografía y ethical hacking.',
    fecha_inicio=date(2026, 6, 1), fecha_termino=date(2026, 6, 30),
    cupo_maximo=10, instructor=inst3, estado='cerrado'
)
c4 = Curso.objects.create(
    nombre='Inteligencia Artificial con Python',
    descripcion='Introducción a machine learning y deep learning con scikit-learn y TensorFlow.',
    fecha_inicio=date(2026, 8, 1), fecha_termino=date(2026, 10, 31),
    cupo_maximo=25, instructor=inst1, estado='activo'
)

# Alumnos
a1 = Alumno.objects.create(nombre='Ana García López', correo='ana@correo.mx',
                             matricula='2021001', telefono='4921111111')
a2 = Alumno.objects.create(nombre='Luis Martínez Torres', correo='luis@correo.mx',
                             matricula='2021002', telefono='4922222222')
a3 = Alumno.objects.create(nombre='María Rodríguez Sánchez', correo='maria@correo.mx',
                             matricula='2021003', telefono='4923333333')

# Usuarios alumno
for alumno, username in [(a1, 'ana'), (a2, 'luis'), (a3, 'maria')]:
    u = User.objects.create_user(username, alumno.correo, 'pass1234',
                                  first_name=alumno.nombre.split()[0],
                                  last_name=' '.join(alumno.nombre.split()[1:]))
    PerfilUsuario.objects.filter(usuario=u).update(tipo='alumno')
    alumno.usuario = u
    alumno.save()

# Inscripciones de prueba
Inscripcion.objects.create(alumno=a1, curso=c1)
Inscripcion.objects.create(alumno=a1, curso=c2)
Inscripcion.objects.create(alumno=a2, curso=c1)
Inscripcion.objects.create(alumno=a3, curso=c4)

print("\nDatos cargados exitosamente:")
print(f"  Instructores: {Instructor.objects.count()}")
print(f"  Cursos:       {Curso.objects.count()}")
print(f"  Alumnos:      {Alumno.objects.count()}")
print(f"  Inscripciones:{Inscripcion.objects.count()}")
print("\nCuentas de prueba (contraseña: pass1234):")
print("  admin   : Administrador  (contrasena: admin1234)")
print("  ana     : Alumno")
print("  luis    : Alumno")
print("  maria   : Alumno")
print("  carlos  : Instructor")
