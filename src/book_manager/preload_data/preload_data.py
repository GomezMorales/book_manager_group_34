
import os
from datetime import date
from pathlib import Path

from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar,
    RepositorioEditorial,
    RepositorioGenero,
    RepositorioLibro,
    RepositorioMoneda,
    RepositorioPrecio,
    RepositorioStock,
    RepositorioTipoCotizacion,
)
from book_manager.services.services import (
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)

RUTA_CSV = Path(__file__).resolve().parent.parent / "migrations" / "csv"

ARCHIVOS = {
    "genero": "generos.csv",
    "editorial": "editoriales.csv",
    "moneda": "monedas.csv",
    "tipo_cotizacion": "tipos_cotizacion.csv",
    "libro": "libros.csv",
    "precio": "precios.csv",
    "stock": "stock.csv",
    "cotizacion": "cotizaciones_dolar.csv",
}

GENEROS = [
    "Novela", "Cuento", "Poesía", "Ensayo", "Ciencia ficción",
    "Fantasía", "Policial", "Historia", "Biografía", "Infantil",
]

EDITORIALES = [
    "Planeta", "Penguin Random House", "Sudamericana", "Emecé", "Alfaguara",
    "Anagrama", "Siglo XXI", "Eudeba", "Minotauro", "Salamandra",
]

MONEDAS = [
    ("ARS", "Peso argentino"),
    ("USD", "Dólar estadounidense"),
    ("EUR", "Euro"),
    ("BRL", "Real brasileño"),
    ("CLP", "Peso chileno"),
    ("UYU", "Peso uruguayo"),
    ("GBP", "Libra esterlina"),
    ("JPY", "Yen japonés"),
    ("MXN", "Peso mexicano"),
    ("CAD", "Dólar canadiense"),
]

TIPOS_COTIZACION = [
    "Oficial", "Blue", "MEP", "CCL", "Tarjeta",
    "Mayorista", "Cripto", "Ahorro", "Turista", "Exportación",
]

# (isbn, título, autor, id de género, id de editorial)
# Los ISBN son ficticios: solo respetan el formato de 13 dígitos.
LIBROS = [
    ("9789500000001", "Metro 2033", "Dmitry Glukhovsky", 5, 1),
    ("9789500000002", "Ficciones", "Jorge Luis Borges", 2, 4),
    ("9789500000003", "Cien años de soledad", "Gabriel García Márquez", 1, 3),
    ("9789500000004", "Harry Potter y la piedra filosofal", "J. K. Rowling", 6, 10),
    ("9789500000005", "El laberinto de la soledad", "Octavio Paz", 4, 1),
    ("9789500000006", "Fahrenheit 451", "Ray Bradbury", 5, 9),
    ("9789500000007", "El señor de los anillos", "J. R. R. Tolkien", 6, 9),
    ("9789500000008", "Asesinato en el Orient Express", "Agatha Christie", 7, 1),
    ("9789500000009", "Las venas abiertas de América Latina", "Eduardo Galeano", 8, 7),
    ("9789500000010", "El principito", "Antoine de Saint-Exupéry", 10, 10),
]

# (id de libro, precio en ARS, precio en USD)
PRECIOS = [
    (1, 28000, 22), (2, 21000, 17), (3, 32000, 25), (4, 15000, 12),
    (5, 24000, 19), (6, 19000, 15), (7, 45000, 36), (8, 18000, 14),
    (9, 26000, 21), (10, 12000, 10),
]

# (id de libro, cantidad)
STOCK = [
    (1, 12), (2, 8), (3, 15), (4, 5), (5, 3),
    (6, 10), (7, 4), (8, 9), (9, 6), (10, 20),
]

# (id de tipo de cotización, fecha, valor). Valores ilustrativos.
COTIZACIONES = [
    (1, date(2026, 9, 14), 1350.0), (1, date(2026, 9, 15), 1355.0),
    (1, date(2026, 9, 16), 1360.0), (1, date(2026, 9, 17), 1358.0),
    (1, date(2026, 9, 18), 1365.0),
    (2, date(2026, 9, 14), 1400.0), (2, date(2026, 9, 15), 1410.0),
    (2, date(2026, 9, 16), 1405.0), (2, date(2026, 9, 17), 1415.0),
    (2, date(2026, 9, 18), 1420.0),
    (3, date(2026, 9, 18), 1390.0), (4, date(2026, 9, 18), 1395.0),
]

def cargar_datos_iniciales(ruta: Path = RUTA_CSV) -> None:
    """Genera los CSV de migrations/csv a partir de los datos iniciales.

    Borra los archivos existentes y vuelve a cargar todo usando los servicios,
    para que los datos pasen por las mismas validaciones que el sistema.
    """
    ruta = Path(ruta)
    os.makedirs(ruta, exist_ok=True)

    # Arranca de cero para no duplicar datos si se ejecuta más de una vez
    for nombre in ARCHIVOS.values():
        archivo = ruta / nombre
        if archivo.exists():
            archivo.unlink()

    # Repositorios apuntando a la carpeta de migraciones
    repo_genero = RepositorioGenero(str(ruta / ARCHIVOS["genero"]))
    repo_editorial = RepositorioEditorial(str(ruta / ARCHIVOS["editorial"]))
    repo_moneda = RepositorioMoneda(str(ruta / ARCHIVOS["moneda"]))
    repo_tipo = RepositorioTipoCotizacion(str(ruta / ARCHIVOS["tipo_cotizacion"]))
    repo_libro = RepositorioLibro(str(ruta / ARCHIVOS["libro"]), repo_genero, repo_editorial)
    repo_precio = RepositorioPrecio(str(ruta / ARCHIVOS["precio"]), repo_libro, repo_moneda)
    repo_stock = RepositorioStock(str(ruta / ARCHIVOS["stock"]), repo_libro)
    repo_cotizacion = RepositorioCotizacionDolar(str(ruta / ARCHIVOS["cotizacion"]), repo_tipo)

    # Catálogos simples (no dependen de otras entidades)
    servicio_genero = ServicioGenero(repo_genero, repo_libro)
    for nombre in GENEROS:
        servicio_genero.crear(nombre)

    servicio_editorial = ServicioEditorial(repo_editorial, repo_libro)
    for nombre in EDITORIALES:
        servicio_editorial.crear(nombre)

    servicio_moneda = ServicioMoneda(repo_moneda, repo_precio)
    for codigo, descripcion in MONEDAS:
        servicio_moneda.crear(codigo, descripcion)

    servicio_tipo = ServicioTipoCotizacion(repo_tipo, repo_cotizacion)
    for nombre in TIPOS_COTIZACION:
        servicio_tipo.crear(nombre)

    # Libros (necesitan géneros y editoriales)
    servicio_libro = ServicioLibro(
        repo_libro, repo_genero, repo_editorial, repo_precio, repo_stock
    )
    for isbn, titulo, autor, genero_id, editorial_id in LIBROS:
        servicio_libro.crear(isbn, titulo, autor, genero_id, editorial_id)

    # Precios en pesos (moneda 1) y en dólares (moneda 2)
    servicio_precio = ServicioPrecio(repo_precio, repo_libro, repo_moneda)
    for libro_id, monto_ars, monto_usd in PRECIOS:
        servicio_precio.crear(libro_id, monto_ars, 1)
        servicio_precio.crear(libro_id, monto_usd, 2)

    # Stock inicial de cada libro
    servicio_stock = ServicioStock(repo_stock, repo_libro)
    for libro_id, cantidad in STOCK:
        servicio_stock.crear(libro_id, cantidad)

    # Cotizaciones del dólar (necesitan tipos de cotización)
    servicio_cotizacion = ServicioCotizacionDolar(repo_cotizacion, repo_tipo)
    for tipo_id, fecha, valor in COTIZACIONES:
        servicio_cotizacion.crear(tipo_id, fecha, valor)
