# Pruebas de integración: reglas de negocio de inscripción

Archivo: `tests/test_inscripciones.py`

Estas pruebas verifican, mediante el cliente de pruebas de Django (peticiones HTTP reales contra las vistas, sin necesidad de un navegador), que las reglas de negocio del módulo de inscripciones funcionan correctamente de extremo a extremo: vista -> formulario/modelo -> base de datos -> mensajes flash.

## Qué cubre cada test

### 1. `test_inscripcion_curso_cancelado`
- Crea un curso con `estado='cancelado'`.
- Un alumno autenticado intenta inscribirse (`POST /inscripciones/inscribirse/<id>/`).
- Verifica que aparece un mensaje flash de error mencionando "cancelado".
- Verifica que **no** se crea ningún registro `Inscripcion` para ese alumno/curso.

### 2. `test_inscripcion_curso_cerrado`
- Crea un curso con `estado='cerrado'`.
- El alumno intenta inscribirse.
- Verifica que la respuesta es una redirección (302) hacia el detalle del curso.
- Verifica que, siguiendo la redirección, aparece un mensaje flash mencionando "cerrado".
- Verifica que **no** se crea la inscripción.

### 3. `test_inscripcion_curso_lleno`
- Crea un curso `activo` con `cupo_maximo=1`.
- Inscribe a un primer alumno (`estado='activa'`), llenando el cupo.
- Confirma que `curso.tiene_cupo()` es `False`.
- Un segundo alumno intenta inscribirse.
- Verifica que aparece un mensaje flash mencionando "cupo".
- Verifica que **no** se crea la inscripción para el segundo alumno.

### 4. `test_carga_evidencia_exitosa`
- Crea un alumno ya inscrito (`estado='activa'`) en un curso activo.
- Sube un archivo PDF válido vía `POST /inscripciones/<id>/evidencia/`.
- Verifica el mensaje flash de éxito ("...exitosamente").
- Recarga la inscripción desde la base de datos y verifica que el campo `evidencia` (Comprobante de inscripción) ahora tiene una ruta de archivo que contiene "comprobante".

### 5. `test_busqueda_y_filtrado_cursos` (RF12)
- Crea dos cursos: "Curso de Django" (activo) y "Curso de Redes" (cerrado).
- Hace `GET /cursos/?q=Django` y verifica que el HTML contiene "Curso de Django" pero **no** "Curso de Redes".
- Hace `GET /cursos/?estado=activo` y verifica el mismo filtrado.

## Cómo correr las pruebas

### 1. Requisitos previos

El proyecto usa **Django 4.2.8**, que no es compatible con Python 3.14. Se recomienda usar **Python 3.12**.

Si no existe el entorno virtual `.venv`, créalo e instala las dependencias:

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Ejecutar solo estas pruebas

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_inscripciones.py -v
```

### 3. Ejecutar una prueba específica

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_inscripciones.py::test_inscripcion_curso_lleno -v
```

## Notas

- Las pruebas usan la base de datos de pruebas que pytest-django crea y destruye automáticamente (no afectan `db.sqlite3`).
- La prueba de carga de evidencia escribe un archivo temporal bajo `media/inscripciones/evidencias/` durante la ejecución (comportamiento normal de `FileField` en pruebas). Si necesitas limpiar archivos generados por pruebas, revisa esa carpeta tras ejecutar.
- Estas pruebas **no** requieren Selenium ni un navegador; para pruebas de interfaz/navegador ver `tests/test_selenium.py`.
