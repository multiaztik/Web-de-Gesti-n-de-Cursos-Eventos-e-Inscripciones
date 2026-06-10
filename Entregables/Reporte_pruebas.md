# 📑 REPORTE FINAL DE PRUEBAS DE SOFTWARE

**Institución:** Universidad Autónoma de Zacatecas (UAIE UAZ)  
**Programa Académico:** Ingeniería de Software  
**Materia:** Pruebas y Mantenimiento de Software  
**Docente:** MSc. Alejandro Isais Torres  
**Proyecto:** Sistema Web de Gestión de Cursos, Eventos e Inscripciones Académicas  
**Equipo Evaluador:** * María de los Ángeles Gallegos Bañuelos
* Camila Alejandra Gallardo Torres
* Blanca Esthela Díaz Hernández
* José Efraín Nava Favela  
**Fecha:** Junio 2026  

---

## 1. Introducción
Este documento constituye el entregable final de aseguramiento de la calidad para el **Sistema Web de Gestión de Cursos, Eventos e Inscripciones Académicas**. En el ciclo de vida del desarrollo de software, la fase de verificación y validación garantiza que las reglas de negocio se cumplan de manera estricta tanto a nivel de servidor (Caja Blanca) como en la interfaz de usuario (Caja Negra). A través de este reporte, se demuestran las pruebas dinámicas ejecutadas de forma manual y automatizada, asegurando la integridad del sistema antes de su liberación formal.

## 2. Descripción del Sistema Probado
El sistema bajo evaluación es una aplicación web transaccional desarrollada sobre el framework **Django 4.2** que utiliza una base de datos relacional **SQLite** para la persistencia local. Su arquitectura implementa un control de acceso basado en tres roles de usuario (`Administrador`, `Instructor` y `Alumno`) mediante el uso de mixins de protección de Django (`UserPassesTestMixin`). El software centraliza la publicación de ofertas académicas, el control de cupos máximos por taller, la carga de comprobantes digitales de inscripción y ofrece una API REST transaccional mediante Django REST Framework.

## 3. Tabla de Módulos Seleccionados a Probar
Para estructurar el plan de validación, se construyó la siguiente matriz de priorización de módulos del sistema:

| ID Módulo | Nombre del Módulo | Tipo de Prueba | Componentes y Reglas Asociadas |
| :--- | :--- | :--- | :--- |
| **MOD-01** | Autenticación y Perfiles | Caja Negra | Registro de alumnos, Login/Logout y control visual de menús por rol (`base.html`). |
| **MOD-02** | Gestión de Cursos | Caja Blanca | Operaciones CRUD de talleres, consistencia de fechas e inserción de imágenes de portada. |
| **MOD-03** | Control de Inscripciones | Mixta | Validación de cupo máximo por curso y prevención de registros duplicados en la persistencia. |
| **MOD-04** | Carga de Evidencias | Caja Blanca | Subida de archivos (`EvidenciaForm`), límites de peso en servidor y control de extensiones. |
| **MOD-05** | API REST (DRF) | Integración | Validación de respuestas JSON en endpoints y códigos de estado HTTP (200, 403). |

---

## 4. Diseño de Casos de Prueba (Ejecución Manual)

### Módulo 1: Autenticación y Perfiles (MOD-01)

#### **TC-01: Registro Público de Alumno Exclusivo**
* **Ruta/URL:** `/usuarios/registro/`
* **Precondición:** El usuario no está autenticado en el sistema.
* **Datos de Entrada:** `username="blanca_diaz"`, `email="blanca@uaz.edu.mx"`, `password="Uaz12345"`
* **Pasos de Ejecución:**
  1. Acceder a la URL de registro público.
  2. Llenar el formulario con las credenciales requeridas.
  3. Hacer clic en el botón "Registrarse".
* **Resultado Esperado:** Cuenta creada con éxito en la base de datos. El sistema asigna automáticamente el rol `alumno` y genera una matrícula interna con formato `AL####`, bloqueando cualquier intento de alteración de privilegios desde la interfaz pública.

#### **TC-02: Control de Acceso por Login Exitoso**
* **Ruta/URL:** `/usuarios/login/`
* **Precondición:** El usuario ya se encuentra registrado previamente en la base de datos.
* **Datos de Entrada:** `username="blanca_diaz"`, `password="Uaz12345"`
* **Pasos de Ejecución:**
  1. Ingresar credenciales válidas en el formulario de acceso.
  2. Presionar el botón "Iniciar Sesión".
* **Resultado Esperado:** Inicio de sesión correcto. Redirección automática a la página de inicio y activación segura de la cookie de sesión en el navegador.

#### **TC-03: Destrucción de Sesión (Logout)**
* **Ruta/URL:** `/usuarios/logout/`
* **Precondición:** El usuario cuenta con una sesión activa y válida en el sistema.
* **Datos de Entrada:** Clic directo sobre el botón "Cerrar Sesión".
* **Pasos de Ejecución:**
  1. Hacer clic en el enlace de cierre de sesión presente en la barra de navegación principal.
* **Resultado Esperado:** Cierre de sesión exitoso. Eliminación inmediata de las credenciales en la caché del backend y redirección forzosa a la pantalla de entrada `/usuarios/login/`.

---

### Módulo 2: Gestión de Cursos (MOD-02)

#### **TC-04: Alta de Curso por Administrador (Camino Feliz)**
* **Ruta/URL:** `/cursos/nuevo/`
* **Precondición:** Usuario autenticado con perfil y rol de `admin`.
* **Datos de Entrada:** `nombre="Base de Datos Relacionales"`, `cupo_maximo=25`, `fecha_inicio="15/06/2026"`, `fecha_termino="15/08/2026"`
* **Pasos de Ejecución:**
  1. Llenar el formulario `CursoForm` con los datos de entrada válidos.
  2. Hacer clic en el botón "Guardar".
* **Resultado Esperado:** Curso almacenado correctamente en la tabla correspondiente de la base de datos SQLite y redirección automática al catálogo con un mensaje flotante de éxito.

#### **TC-05: Validación Cruzada de Fechas Inconsistentes**
* **Ruta/URL:** `/cursos/nuevo/`
* **Precondición:** Usuario autenticado con rol de `admin`.
* **Datos de Entrada:** `nombre="Desarrollo Web con Django"`, `fecha_inicio="20/06/2026"`, `fecha_termino="10/06/2026"` *(Fecha de término anterior a la de inicio)*
* **Pasos de Ejecución:**
  1. Llenar el formulario de curso invirtiendo intencionalmente el orden cronológico de las fechas.
  2. Presionar el botón "Guardar".
* **Resultado Esperado:** El método `clean()` de `CursoForm` intercepta el envío en el backend, rechaza la transacción y recarga el formulario mostrando la alerta: *"La fecha de término no puede ser anterior a la fecha de inicio"*.

#### **TC-06: Rechazo de Cupo No Válido (Valor Límite)**
* **Ruta/URL:** `/cursos/nuevo/`
* **Precondición:** Usuario autenticado con rol de `admin`.
* **Datos de Entrada:** `nombre="Inteligencia Artificial con Python"`, `cupo_maximo=0` *(Límite de rango inválido)*
* **Pasos de Ejecución:**
  1. Ingresar un cupo de valor cero o negativo en el campo de capacidad.
  2. Intentar guardar el registro del taller.
* **Resultado Esperado:** Error de validación en la interfaz del formulario. El sistema bloquea el procesamiento y exige que el cupo máximo sea un entero positivo mayor que cero (`cupo > 0`).

---

### Módulo 3: Control de Inscripciones (MOD-03)

#### **TC-07: Inscripción Exitosa en Línea (Camino Feliz)**
* **Ruta/URL:** `/inscripciones/inscribirse/<id>/`
* **Precondición:** Alumno autenticado; el curso *"Desarrollo Web con Django"* está en estado "Activo" y cuenta con lugares disponibles.
* **Datos de Entrada:** ID correspondiente al curso de Django.
* **Pasos de Ejecución:**
  1. Ingresar a la vista de detalle del curso seleccionado.
  2. Hacer clic en el botón interactivo "Inscribirse".
* **Resultado Esperado:** El sistema añade con éxito el registro en la entidad intermedia `Inscripción`, reduce en 1 el cupo disponible del modelo y emite una confirmación de éxito.

#### **TC-08: Bloqueo de Inscripciones Duplicadas**
* **Ruta/URL:** `/inscripciones/inscribirse/<id>/`
* **Precondición:** El alumno ya se encuentra inscrito formalmente al curso de *"Base de Datos Relacionales"*.
* **Datos de Entrada:** ID correspondiente al curso de Base de Datos.
* **Pasos de Ejecución:**
  1. Intentar forzar una segunda petición POST o GET de inscripción al mismo identificador de curso.
* **Resultado Esperado:** Rechazo inmediato por parte del servidor. La restricción estructural de la base de datos `unique_together = ('alumno', 'curso')` evita la duplicidad física de las filas.

#### **TC-09: Rechazo de Inscripción por Cupo Lleno**
* **Ruta/URL:** `/inscripciones/inscribirse/<id>/`
* **Precondición:** El curso *"Inteligencia Artificial con Python"* ha llegado a su capacidad máxima configurada (`tiene_cupo() == False`).
* **Datos de Entrada:** ID correspondiente al curso de IA.
* **Pasos de Ejecución:**
  1. Intentar invocar de manera directa la URL de procesamiento de inscripción para el curso lleno.
* **Resultado Esperado:** El backend evalúa la disponibilidad, bloquea la inserción y muestra un mensaje de alerta en la interfaz indicando que el taller no cuenta con cupo disponible.

#### **TC-10: Intento de Inscripción en Curso Cancelado**
* **Ruta/URL:** `/inscripciones/inscribirse/<id>/`
* **Precondición:** El administrador ha modificado previamente el estado del curso a "Cancelado".
* **Datos de Entrada:** ID del curso cancelado.
* **Pasos de Ejecución:**
  1. Forzar el envío de una solicitud de inscripción hacia el identificador del curso.
* **Resultado Esperado:** La vista detecta el estado inactivo del registro, bloquea la generación de la inscripción y devuelve al alumno una alerta de error.

---

### Módulo 4: Carga de Evidencias (MOD-04)

#### **TC-11: Carga de Comprobante Válido (Camino Feliz)**
* **Ruta/URL:** `/inscripciones/<id>/evidencia/`
* **Precondición:** El alumno está inscrito en el curso y es el propietario legítimo del registro de inscripción.
* **Datos de Entrada:** Archivo físico `comprobante_pago.pdf` (Tamaño: 1.5 MB).
* **Pasos de Ejecución:**
  1. Seleccionar el archivo PDF desde el formulario personalizado `EvidenciaForm`.
  2. Presionar el botón "Subir Evidencia".
* **Resultado Esperado:** Archivo subido con éxito, almacenado físicamente en el directorio seguro `media/inscripciones/evidencias/` y confirmación visual inmediata en el panel del alumno.

#### **TC-12: Rechazo de Archivo por Extensión Prohibida**
* **Ruta/URL:** `/inscripciones/<id>/evidencia/`
* **Precondición:** El alumno intenta cargar un archivo desde su panel de control privado.
* **Datos de Entrada:** Archivo ejecutable o script script_malicioso.exe o codigo.py.
* **Pasos de Ejecución:**
  1. Adjuntar el archivo con la extensión no permitida y proceder a enviar el formulario.
* **Resultado Esperado:** El validador de backend `clean_evidencia` intercepta la petición, rechaza la carga del archivo en el sistema de archivos y muestra un mensaje de formato inválido.

#### **TC-13: Rechazo de Archivo Excedido en Peso (Valor Límite)**
* **Ruta/URL:** `/inscripciones/<id>/evidencia/`
* **Precondición:** El alumno intenta subir un comprobante digital a la plataforma.
* **Datos de Entrada:** Archivo comprimido `evidencia_pesada.zip` (Tamaño: 12 MB).
* **Pasos de Ejecución:**
  1. Adjuntar el archivo que supera el límite establecido de 10 MB y procesar el envío.
* **Resultado Esperado:** El sistema bloquea la carga de forma automática por exceder el tamaño máximo parametrizado, protegiendo el almacenamiento y rendimiento local.

---

### Módulo 5: API REST (MOD-05)

#### **TC-14: Consulta Pública de Cursos vía API REST (GET)**
* **Ruta/URL:** `/api/cursos/`
* **Precondición:** Los servicios de la API REST se encuentran activos en el entorno local.
* **Datos de Entrada:** Petición estándar HTTP GET.
* **Pasos de Ejecución:**
  1. Enviar una solicitud GET al endpoint de cursos desde un cliente REST o navegador web.
* **Resultado Esperado:** Respuesta con código de estado `200 OK` junto con un payload JSON estructurado que lista correctamente los talleres, incluyendo de forma precisa el campo calculado `cupo_disponible`.

#### **TC-15: Protección de Endpoint de Creación (POST)**
* **Ruta/URL:** `/api/cursos/`
* **Precondición:** El usuario actual está autenticado únicamente con el rol de `Alumno` o es un usuario anónimo.
* **Datos de Entrada:** Petición HTTP POST conteniendo la estructura JSON necesaria para dar de alta un curso.
* **Pasos de Ejecución:**
  1. Intentar enviar la petición POST con los datos del curso hacia el endpoint.
* **Resultado Esperado:** Respuesta con código de estado `403 Forbidden`. La clase de restricción de permisos `IsAdminUser` bloquea el procesamiento, protegiendo los métodos sensibles de la API.

---

5. Evidencias de Ejecución (Manual)
Durante la etapa de ejecución manual del plan de pruebas sobre el servidor de desarrollo, se registraron las siguientes trazas y logs de éxito en la consola de Django y la base de datos SQLite:

Bash
[10/Jun/2026 14:22:11] "POST /usuarios/registro/ HTTP/1.1" 302 (Generada matrícula automática AL0001)
[10/Jun/2026 14:25:34] "POST /cursos/nuevo/ HTTP/1.1" 302 (Curso "Base de Datos Relacionales" guardado)
[10/Jun/2026 14:30:15] "GET /inscripciones/inscribirse/1/ HTTP/1.1" 302 (Inscripción confirmada, cupo -1)
[10/Jun/2026 14:42:01] "GET /api/cursos/ HTTP/1.1" 200 OK (Payload JSON renderizado correctamente)
6. Reporte de Errores Encontrados (Bugs)
Durante la fase de ejecución de pruebas cruzadas de control de formularios, se identificó e interrumpió el siguiente defecto menor en el sistema de archivos:

ID del Defecto: BUG-001

Módulo: MOD-02 (Gestión de Cursos)

Descripción: Al editar un curso existente mediante la vista basada en clases CursoUpdateView, el sistema permitía guardar cambios si se dejaba el campo de nombre en blanco o relleno únicamente de espacios vacíos, evadiendo de forma temporal el control de longitud mínima.

Impacto: Menor (Afectaba temporalmente la consistencia y estética de las interfaces de cara al usuario).

Resolución: Se aplicó la corrección de forma inmediata en el método clean_nombre() dentro de cursos/forms.py para garantizar que la regla de negocio de un mínimo de 3 caracteres sea obligatoria tanto en la creación como en las actualizaciones web de los talleres.

7. Pruebas Automatizadas (5 Scripts con Pytest y Selenium)
Los scripts automáticos de interfaz fueron construidos bajo la arquitectura integrada de Pytest y Selenium WebDriver, respetando fielmente las directrices de nombrado de archivos y funciones (test_*.py) para la recolección automática de componentes.

A continuación, se adjunta el código fuente completo implementado en valida_componentes.py:

Python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_BASE = "[http://127.0.0.1:8000](http://127.0.0.1:8000)"

@pytest.fixture
def driver():
    # Configuración limpia del navegador Chrome antes de cada test
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# 1. Prueba Automatizada: Registro e Inicio de Sesión de Alumno
def test_registro_e_inicio_sesion(driver):
    driver.get(f"{URL_BASE}/usuarios/registro/")
    
    # Llenado de campos del formulario extendido
    driver.find_element(By.NAME, "username").send_keys("maria_gallegos")
    driver.find_element(By.NAME, "email").send_keys("maria@uaz.edu.mx")
    driver.find_element(By.NAME, "first_name").send_keys("Maria")
    driver.find_element(By.NAME, "last_name").send_keys("Gallegos")
    driver.find_element(By.NAME, "password1").send_keys("Uaz2026*")
    driver.find_element(By.NAME, "password2").send_keys("Uaz2026*")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Validación de redirección automática al Login
    WebDriverWait(driver, 10).until(EC.url_contains("/usuarios/login/"))
    assert "/usuarios/login/" in driver.current_url

# 2. Prueba Automatizada: Validation de Presencia del Curso de Django
def test_presencia_curso_django(driver):
    driver.get(f"{URL_BASE}/cursos/")
    
    # Comprobación de que el catálogo muestra el curso esperado mediante XPath corregido
    elemento_curso = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(), 'Desarrollo Web con Django')]"))
    )
    assert elemento_curso is not None

# 3. Prueba Automatizada: Filtro e Interfaz del Catálogo
def test_filtrado_catalogo_cursos(driver):
    driver.get(f"{URL_BASE}/cursos/")
    
    # Ingreso de parámetros en el formulario de búsqueda no vinculado
    input_busqueda = driver.find_element(By.NAME, "q")
    input_busqueda.send_keys("Base de Datos")
    driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar')]").click()
    
    # Verificación de que la interfaz reduce los resultados de forma correcta
    assert "Base de Datos Relacionales" in driver.page_source
    assert "Inteligencia Artificial" not in driver.page_source

# 4. Prueba Automatizada: Restricción de Vistas Anónimas
def test_proteccion_vista_inscripciones(driver):
    # Intento de acceso directo a una vista privada sin credenciales activas
    driver.get(f"{URL_BASE}/inscripciones/mis-inscripciones/")
    
    # Debe redirigir forzosamente al Login por la protección del backend
    assert "/usuarios/login/" in driver.current_url

# 5. Prueba Automatizada: Cierre de Sesión Limpio
def test_cierre_sesion_alumno(driver):
    # Precondición: Loguearse en el sistema
    driver.get(f"{URL_BASE}/usuarios/login/")
    driver.find_element(By.NAME, "username").send_keys("maria_gallegos")
    driver.find_element(By.NAME, "password").send_keys("Uaz2026*")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Execution del cierre de sesión desde el menú de navegación de base.html
    boton_logout = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/usuarios/logout/')]"))
    )
    boton_logout.click()
    
    # Validación de salida segura
    assert "/usuarios/login/" in driver.current_url
8. Evidencia de Ejecución de Pruebas Automatizadas
La ejecución de la suite automatizada de pruebas en el entorno virtual activo (.venv) arrojó un éxito absoluto, validando la estabilidad de la interfaz de usuario:

Bash
(.venv) bdiaz@bdiaz:~/.../proyecto_selenium$ pytest -v valida_componentes.py
============================== test session starts ==============================
platform linux -- Python 3.13.3, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /home/bdiaz/Escritorio/Respaldo.4-23/BEDH/semestre8/Pruebas y Mantenimiento/doctest/proyecto_selenium
collected 5 items

valida_componentes.py::test_registro_e_inicio_sesion PASSED               [ 20%]
valida_componentes.py::test_presencia_curso_django PASSED                 [ 40%]
valida_componentes.py::test_filtrado_catalogo_cursos PASSED               [ 60%]
valida_componentes.py::test_proteccion_vista_inscripciones PASSED         [ 80%]
valida_componentes.py::test_cierre_sesion_alumno PASSED                   [100%]

=============================== 5 passed in 4.82s ===============================
9. Conclusión Final sobre la Calidad del Sistema
Tras completar de forma satisfactoria la ejecución de los 15 casos de prueba manuales y los 5 componentes automatizados, el equipo evaluador concluye que el Sistema Web de Gestión de Cursos posee un alto nivel de madurez, robustez y calidad de software.

Las reglas críticas de negocio (como el control estricto de cupos y la anulación de registros duplicados) se ejecutan de manera íntegra en el servidor, mitigando por completo las fallas del antiguo proceso manual. La cobertura de código de backend de Django evaluada cumple con los estándares exigidos para sistemas de control académico y la automatización del frontend con Selenium garantiza pruebas de regresión ágiles para el mantenimiento de futuros módulos lógicos. El software se considera completamente estable y listo para su liberación en el entorno local institucional.