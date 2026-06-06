def es_palindromo(s):
    """
    Devuelve True si la cadena es un palíndromo.
    TIP: convierte a minúsculas y quita espacios.

    >>> es_palindromo("Anita lava la tina")
    True
    >>> es_palindromo("python")
    False
    """
    limpio = s.lower().replace(" ", "")
    return limpio == limpio[::-1]


def promedio(lista):
    """
    Devuelve el promedio de una lista de números.
    Lanza ValueError si la lista está vacía.

    >>> promedio([10, 8, 9])
    9.0
    >>> promedio([])
    Traceback (most recent call last):
    ValueError: La lista está vacía
    """
    if not lista:
        raise ValueError("La lista está vacía")
    return sum(lista) / len(lista)


def normalizar_texto(s):
    """
    Convierte el texto a minúsculas y elimina espacios extra.

    >>> normalizar_texto("  HOLA Mundo  ")
    'hola mundo'
    """
    return s.lower().strip()


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
