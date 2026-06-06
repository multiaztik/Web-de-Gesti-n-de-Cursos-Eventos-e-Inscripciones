---
name: project-scea
description: Proyecto Final Django UAZ — Sistema de Gestión de Cursos, Eventos e Inscripciones Académicas
metadata:
  type: project
---

Sistema Django completo construido según especificaciones del PDF "Proyecto Final" de la UAZ (Programación Delphi/Web 2026).

**Why:** Proyecto final académico con requerimientos específicos del PDF entregado por el maestro.

**How to apply:** Toda modificación debe cumplir los RFs y RNFs del PDF. No romper validaciones de negocio (cupo, duplicados, autenticación).

## Estructura

- `sistema_cursos/` — configuración Django (settings, urls raíz)
- `usuarios/` — modelos PerfilUsuario, Alumno, Instructor + CRUD + autenticación
- `cursos/` — modelo Curso + CBVs + forms + serializers + api_views
- `inscripciones/` — modelo Inscripcion + vistas de inscripción, evidencia, alumnos inscritos
- `templates/` — base.html con Bootstrap 5 + todos los templates por app
- `media/` — archivos subidos (ignorado en git)

## Cuentas de prueba (BD actual)

- `admin` / `admin1234` — superusuario administrador
- `ana`, `luis`, `maria` / `pass1234` — alumnos
- `carlos` / `pass1234` — instructor

## Endpoints API REST

- `/api/cursos/`, `/api/alumnos/`, `/api/inscripciones/`, `/api/instructores/`
- `/api/cursos/{id}/inscritos/` — endpoint extra

## Comandos

```
python manage.py runserver
python poblar_datos.py   # carga datos de prueba
```
