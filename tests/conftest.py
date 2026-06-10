import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_cursos.settings")

@pytest.fixture
def driver():
    options = ChromeOptions()
    if os.environ.get("HEADLESS") == "true":
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    yield driver
    
    driver.quit()

@pytest.fixture
def setup_datos(db):
    """Fixture para poblar la base de datos de pruebas con instructor y curso."""
    from usuarios.models import Instructor
    from cursos.models import Curso
    from datetime import date
    
    instructor = Instructor.objects.create(
        nombre='Dr. Alejandro Isais', 
        correo='alejandro@pruebas.com',
        especialidad='Programación Delphi', 
        telefono='4921234567'
    )
    
    curso = Curso.objects.create(
        nombre='Desarrollo Web con Django',
        descripcion='Aprende a construir aplicaciones web completas usando Django y Python.',
        fecha_inicio=date(2026, 7, 1), 
        fecha_termino=date(2026, 8, 31),
        cupo_maximo=20, 
        instructor=instructor, 
        estado='activo'
    )
    
    return instructor, curso
