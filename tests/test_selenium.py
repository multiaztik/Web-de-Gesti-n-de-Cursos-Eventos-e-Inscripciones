import os
import tempfile
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, Alumno
from inscripciones.models import Inscripcion

@pytest.mark.django_db(transaction=True)
def test_registro_e_inicio_sesion(driver, live_server):
    """
    Registro e inicio de sesión:
    - Registro de un nuevo alumno.
    - Redirección/Navegación al logout y luego al login.
    - Inicio de sesión con el nuevo usuario.
    - Validación de que está dentro del sistema (comprobación de barra de navegación y perfil).
    """
    driver.get(f"{live_server.url}/usuarios/registro/")
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    driver.find_element(By.NAME, "username").send_keys("camila_gallardo")
    driver.find_element(By.NAME, "first_name").send_keys("Camila")
    driver.find_element(By.NAME, "last_name").send_keys("Gallardo")
    driver.find_element(By.NAME, "email").send_keys("camila@pruebas.com")
    driver.find_element(By.NAME, "password1").send_keys("SecretPass998!")
    driver.find_element(By.NAME, "password2").send_keys("SecretPass998!")
    
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.url_to_be(f"{live_server.url}/")
    )
    alert = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )
    assert "creada exitosamente" in alert.text
    assert "Camila" in alert.text
    
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.dropdown-toggle"))
    )
    dropdown.click()
    
    logout_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Cerrar Sesión')]"))
    )
    logout_btn.click()
    
    WebDriverWait(driver, 10).until(
        EC.url_contains("/usuarios/login/")
    )
    alert_info = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-info"))
    )
    assert "cerrado sesión correctamente" in alert_info.text
    
    driver.find_element(By.NAME, "username").send_keys("camila_gallardo")
    driver.find_element(By.NAME, "password").send_keys("SecretPass998!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.url_to_be(f"{live_server.url}/")
    )
    welcome_alert = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )
    assert "Bienvenido de nuevo, Camila" in welcome_alert.text
    
    navbar_user = driver.find_element(By.CSS_SELECTOR, "a.dropdown-toggle").text
    assert "Camila Gallardo" in navbar_user


@pytest.mark.django_db(transaction=True)
def test_inscripcion_visual(driver, live_server, setup_datos):
    """
    Inscripción visual:
    - Iniciar sesión como alumno.
    - Navegar al catálogo de cursos.
    - Clic en 'Ver' un curso y luego en 'Inscribirse ahora'.
    - Verificar que redirige a mis inscripciones con alerta de éxito.
    """
    user = User.objects.create_user(
        username="maria_gallegos",
        email="maria@pruebas.com",
        password="Password123!",
        first_name="María",
        last_name="Gallegos"
    )
    PerfilUsuario.objects.create(usuario=user, tipo='alumno')
    Alumno.objects.create(
        usuario=user,
        nombre="María Gallegos",
        correo=user.email,
        matricula="AL9999",
        telefono="4920000000"
    )
    
    driver.get(f"{live_server.url}/usuarios/login/")
    driver.find_element(By.NAME, "username").send_keys("maria_gallegos")
    driver.find_element(By.NAME, "password").send_keys("Password123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.url_to_be(f"{live_server.url}/")
    )
    
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Cursos')]"))
    ).click()
    
    ver_curso_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'card')][.//h5[contains(., 'Desarrollo Web con Django')]]//a[contains(., 'Ver')]"))
    )
    ver_curso_btn.click()
    
    inscribirse_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inscribirse ahora')]"))
    )
    inscribirse_btn.click()
    
    WebDriverWait(driver, 10).until(
        EC.url_contains("/inscripciones/mis-inscripciones/")
    )
    alert = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )
    assert "Te has inscrito exitosamente" in alert.text
    assert "Desarrollo Web con Django" in alert.text


@pytest.mark.django_db(transaction=True)
def test_subida_archivo(driver, live_server, setup_datos):
    """
    Subida de archivo:
    - Crear alumno y una inscripción activa programáticamente.
    - Iniciar sesión.
    - Ir a 'Mis inscripciones'.
    - Cargar una imagen de evidencia.
    - Verificar la confirmación de carga y actualización visual.
    """
    _, curso = setup_datos
    user = User.objects.create_user(
        username="blanca_diaz",
        email="blanca@pruebas.com",
        password="Password123!",
        first_name="Blanca",
        last_name="Díaz"
    )
    PerfilUsuario.objects.create(usuario=user, tipo='alumno')
    alumno = Alumno.objects.create(
        usuario=user,
        nombre="Blanca Díaz",
        correo=user.email,
        matricula="AL8888",
        telefono="4920000000"
    )
    Inscripcion.objects.create(alumno=alumno, curso=curso)
    
    driver.get(f"{live_server.url}/usuarios/login/")
    driver.find_element(By.NAME, "username").send_keys("blanca_diaz")
    driver.find_element(By.NAME, "password").send_keys("Password123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.url_to_be(f"{live_server.url}/")
    )
    
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Mis Inscripciones')]"))
    ).click()
    
    subir_evidencia_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Subir evidencia')]"))
    )
    subir_evidencia_btn.click()
    
    temp_file, temp_file_path = tempfile.mkstemp(suffix=".png")
    try:
        with os.fdopen(temp_file, 'wb') as tmp:
            tmp.write(b"Fake PNG image bytes")
            
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_evidencia"))
        )
        file_input.send_keys(temp_file_path)
        
        driver.find_element(By.XPATH, "//button[@type='submit'][contains(., 'Subir')]").click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/inscripciones/mis-inscripciones/")
        )
        alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Evidencia subida exitosamente" in alert.text
        
        info_evidencia = driver.find_element(By.XPATH, "//div[contains(@class, 'card')][.//h5[contains(text(), 'Desarrollo Web con Django')]]//p[contains(., 'Evidencia')]")
        assert "Evidencia subida" in info_evidencia.text
        
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@pytest.mark.django_db(transaction=True)
def test_cierre_sesion(driver, live_server):
    """
    Cierre de sesión:
    - Iniciar sesión como alumno.
    - Clic en el botón dropdown y en 'Cerrar Sesión'.
    - Verificar que es redirigido al login.
    - Intentar acceder directamente a una url protegida ('/inscripciones/mis-inscripciones/').
    - Verificar que es redirigido al login y no tiene acceso a las páginas privadas.
    """
    user = User.objects.create_user(
        username="jose_nava",
        email="jose@pruebas.com",
        password="Password123!",
        first_name="José",
        last_name="Nava"
    )
    PerfilUsuario.objects.create(usuario=user, tipo='alumno')
    Alumno.objects.create(
        usuario=user,
        nombre="José Nava",
        correo=user.email,
        matricula="AL7777",
        telefono="4920000000"
    )
    
    driver.get(f"{live_server.url}/usuarios/login/")
    driver.find_element(By.NAME, "username").send_keys("jose_nava")
    driver.find_element(By.NAME, "password").send_keys("Password123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.url_to_be(f"{live_server.url}/")
    )
    
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.dropdown-toggle"))
    )
    dropdown.click()
    
    logout_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Cerrar Sesión')]"))
    )
    logout_btn.click()
    
    WebDriverWait(driver, 10).until(
        EC.url_contains("/usuarios/login/")
    )
    
    driver.get(f"{live_server.url}/inscripciones/mis-inscripciones/")
    
    WebDriverWait(driver, 10).until(
        EC.url_contains("/usuarios/login/")
    )
    
    assert "next=/inscripciones/mis-inscripciones/" in driver.current_url
