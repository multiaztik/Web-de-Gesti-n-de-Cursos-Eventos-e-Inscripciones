# ============================================================
# Pruebas Fundamentales de Mantenimiento con doctest
# ============================================================
# Este archivo contiene las 4 pruebas fundamentales vistas en clase:
#   1. Prueba de Éxito (Área de Rectángulo)
#   2. Prueba con Error (Simulación de Fallo)
#   3. Prueba de Excepciones (Dividir)
#   4. Prueba de Lógica Booleana (Es Par)
# ============================================================


# --- 1. Prueba de Éxito (Área de Rectángulo) ---
# Esta prueba valida que el módulo compare la salida real
# con la esperada y pase correctamente.

def area_rectangulo(base, altura):
    """
    Calcula el área de un rectángulo.
    >>> area_rectangulo(3, 4)
    12
    >>> area_rectangulo(5, 2)
    10
    """
    return base * altura


# --- 2. Prueba con Error (Simulación de Fallo) ---
# Aquí cambiamos el resultado esperado a propósito para ver
# cómo doctest reporta un error.
# Al ejecutarlo, doctest dirá: "Expected: 15, Got: 12"

def area_rectangulo_con_error(base, altura):
    """
    >>> area_rectangulo_con_error(3, 4)
    15
    """
    return base * altura


# --- 3. Prueba de Excepciones (Dividir) ---
# Esta prueba es crucial porque enseña cómo capturar errores
# como la división por cero usando el Traceback.

def dividir(a, b):
    """
    >>> dividir(10, 2)
    5.0
    >>> dividir(1, 0)
    Traceback (most recent call last):
    ZeroDivisionError: division by zero
    """
    return a / b


# --- 4. Prueba de Lógica Booleana (Es Par) ---
# Verifica si un número es par o impar, una prueba clásica
# de lógica de control.

def es_par(n):
    """
    Devuelve True si el número es par, False si es impar.
    >>> es_par(4)
    True
    >>> es_par(7)
    False
    >>> es_par(-2)
    True
    """
    return n % 2 == 0


# ============================================================
# Ejecución de las pruebas
# ============================================================
# Resumen del flujo de trabajo en clase:
#   1. Escribir el código: Se incluye el ejemplo dentro de las
#      comillas triples (""") del docstring.
#   2. Importar el módulo: Se usa import doctest al final.
#   3. Ejecutar: Se usa doctest.testmod(verbose=True) para ver
#      el detalle de cada prueba.
# ============================================================

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
