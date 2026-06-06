import urllib.request
r = urllib.request.urlopen('http://127.0.0.1:8000/')
html = r.read().decode()
# Check for table and courses
if '<table>' in html:
    print('La tabla de cursos esta presente en la pagina')
if 'Desarrollo Web con Django' in html:
    print('Curso "Desarrollo Web con Django" encontrado')
if 'Bases de Datos con MySQL' in html:
    print('Curso "Bases de Datos con MySQL" encontrado')
if 'Programacion en Python' in html or 'oacute' in html:
    print('Curso "Programacion en Python" encontrado')
if 'Inteligencia Artificial' in html:
    print('Curso "Inteligencia Artificial" encontrado')
if 'Redes y Seguridad' in html:
    print('Curso "Redes y Seguridad Informatica" encontrado')
print(f'\nTotal de caracteres HTML: {len(html)}')
