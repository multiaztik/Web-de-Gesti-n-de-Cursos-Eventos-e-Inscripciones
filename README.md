# Sistema Web de Gestión de Cursos, Eventos e Inscripciones Académicas

Aplicación web desarrollada en **Django 4.2** para administrar cursos y eventos académicos, instructores, alumnos e inscripciones. Incluye una **API REST** construida con Django REST Framework.

## Descripción

Una institución educativa necesita centralizar la gestión de sus cursos y eventos. Este sistema permite:

- Registrar y autenticar usuarios con tres roles: **Administrador**, **Instructor** y **Alumno**
- Administrar cursos con cupo, estado, fechas e imagen
- Inscribir alumnos a cursos con validación de cupo y duplicados
- Subir evidencias o comprobantes por inscripción
- Consultar alumnos inscritos por curso (admin/instructor)
- Buscar y filtrar cursos por nombre, instructor o estado
- Consumir y manipular datos mediante una API REST

## Tecnologías

- Python 3.x
- Django 4.2
- Django REST Framework 3.17
- Pillow 12.x (manejo de imágenes)
- SQLite (base de datos local)
- Bootstrap 5.3 (interfaz)

## Estructura del proyecto

```
├── sistema_cursos/      # Configuración principal (settings, urls)
├── usuarios/            # Modelos: PerfilUsuario, Alumno, Instructor + autenticación + CRUD
├── cursos/              # Modelo Curso + vistas CBV + formularios + serializers + API
├── inscripciones/       # Modelo Inscripcion + inscripción, evidencias, lista inscritos
├── templates/           # Plantillas HTML con Bootstrap 5
├── static/              # Archivos estáticos (CSS, JS)
├── media/               # Archivos subidos por usuarios (generado al correr)
├── dev/                 # Código base de referencia (Tarea1, uaz_frameworks)
├── poblar_datos.py      # Script para cargar datos de prueba
├── manage.py
└── requirements.txt
```

## Requisitos previos

- Python 3.10 o superior
- pip

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/multiaztik/Web-de-Gesti-n-de-Cursos-Eventos-e-Inscripciones.git
cd Web-de-Gesti-n-de-Cursos-Eventos-e-Inscripciones
```

### 2. Crear y activar el entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. (Opcional) Cargar datos de prueba

```bash
python poblar_datos.py
```

Esto crea instructores, cursos e inscripciones de ejemplo, además de las siguientes cuentas:

| Usuario  | Contraseña  | Rol           |
|----------|-------------|---------------|
| admin    | admin1234   | Administrador |
| ana      | pass1234    | Alumno        |
| luis     | pass1234    | Alumno        |
| maria    | pass1234    | Alumno        |
| carlos   | pass1234    | Instructor    |

### 6. Crear superusuario (si no se usó el script anterior)

```bash
python manage.py createsuperuser
```

### 7. Iniciar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Vistas principales

| URL | Descripción |
|-----|-------------|
| `/` | Página de inicio |
| `/cursos/` | Lista de cursos con búsqueda y filtros |
| `/cursos/<id>/` | Detalle del curso e inscripción |
| `/cursos/nuevo/` | Crear curso (admin) |
| `/usuarios/registro/` | Registro de nuevos usuarios |
| `/usuarios/login/` | Inicio de sesión |
| `/usuarios/perfil/` | Perfil del usuario autenticado |
| `/usuarios/alumnos/` | Gestión de alumnos (admin) |
| `/usuarios/instructores/` | Gestión de instructores (admin) |
| `/inscripciones/mis-inscripciones/` | Cursos en los que está inscrito el alumno |
| `/inscripciones/<id>/evidencia/` | Subir evidencia de inscripción |
| `/admin/` | Panel de administración de Django |

## API REST

Base URL: `/api/`

| Endpoint | Métodos | Descripción |
|----------|---------|-------------|
| `/api/cursos/` | GET, POST | Lista y creación de cursos |
| `/api/cursos/<id>/` | GET, PUT, PATCH, DELETE | Detalle de curso |
| `/api/cursos/<id>/inscritos/` | GET | Alumnos inscritos en el curso |
| `/api/alumnos/` | GET, POST | Lista y creación de alumnos |
| `/api/alumnos/<id>/` | GET, PUT, PATCH, DELETE | Detalle de alumno |
| `/api/inscripciones/` | GET, POST | Lista y creación de inscripciones |
| `/api/instructores/` | GET, POST | Lista y creación de instructores |

La API es navegable desde el propio navegador en [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

## Reglas de negocio principales

1. Un alumno no puede inscribirse dos veces al mismo curso
2. Un curso no acepta más alumnos que su cupo máximo
3. Un curso cancelado no permite nuevas inscripciones
4. La fecha de término debe ser posterior o igual a la de inicio
5. Solo usuarios autenticados pueden inscribirse
6. Solo administradores o instructores pueden ver la lista completa de inscritos
7. Solo administradores pueden crear, editar o eliminar cursos
