from datetime import date

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    CotizacionDolar as ModeloCotizacionDolar,
    Editorial as ModeloEditorial,
    Genero as ModeloGenero,
    Libro as ModeloLibro,
    Moneda as ModeloMoneda,
    Precio as ModeloPrecio,
    Stock as ModeloStock,
    TipoCotizacion as ModeloTipoCotizacion,
)

GENEROS = [
    "Novela",
    "Cuento",
    "Poesía",
    "Ensayo",
    "Ciencia ficción",
    "Fantasía",
    "Policial",
    "Historia",
    "Biografía",
    "Infantil",
]

EDITORIALES = [
    "Planeta",
    "Penguin Random House",
    "Sudamericana",
    "Emecé",
    "Alfaguara",
    "Anagrama",
    "Siglo XXI",
    "Eudeba",
    "Minotauro",
    "Salamandra",
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
    "Oficial",
    "Blue",
    "MEP",
    "CCL",
    "Tarjeta",
    "Mayorista",
    "Cripto",
    "Ahorro",
    "Turista",
    "Exportación",
]

# (isbn, título, autor, id de género, id de editorial)
# Los ISBN son ficticios: solo respetan el formato de 13 dígitos.
LIBROS = [
    ("9789500000001", "Metro 2033", "Dmitry Glukhovsky", 5, 1),
    ("9789500000002", "Ficciones", "Jorge Luis Borges", 2, 4),
    ("9789500000003", "Cien años de soledad", "Gabriel García Márquez", 1, 3),
    (
        "9789500000004",
        "Harry Potter y la piedra filosofal",
        "J. K. Rowling",
        6,
        10,
    ),
    ("9789500000005", "El laberinto de la soledad", "Octavio Paz", 4, 1),
    ("9789500000006", "Fahrenheit 451", "Ray Bradbury", 5, 9),
    ("9789500000007", "El señor de los anillos", "J. R. R. Tolkien", 6, 9),
    (
        "9789500000008",
        "Asesinato en el Orient Express",
        "Agatha Christie",
        7,
        1,
    ),
    (
        "9789500000009",
        "Las venas abiertas de América Latina",
        "Eduardo Galeano",
        8,
        7,
    ),
    ("9789500000010", "El principito", "Antoine de Saint-Exupéry", 10, 10),
]

# (id de libro, precio en ARS, precio en USD)
PRECIOS = [
    (1, 28000, 22),
    (2, 21000, 17),
    (3, 32000, 25),
    (4, 15000, 12),
    (5, 24000, 19),
    (6, 19000, 15),
    (7, 45000, 36),
    (8, 18000, 14),
    (9, 26000, 21),
    (10, 12000, 10),
]

# (id de libro, cantidad)
STOCK = [
    (1, 12),
    (2, 8),
    (3, 15),
    (4, 5),
    (5, 3),
    (6, 10),
    (7, 4),
    (8, 9),
    (9, 6),
    (10, 20),
]

# (id de tipo de cotización, fecha, valor). Valores ilustrativos.
COTIZACIONES = [
    (1, date(2026, 9, 14), 1350.0),
    (1, date(2026, 9, 15), 1355.0),
    (1, date(2026, 9, 16), 1360.0),
    (1, date(2026, 9, 17), 1358.0),
    (1, date(2026, 9, 18), 1365.0),
    (2, date(2026, 9, 14), 1400.0),
    (2, date(2026, 9, 15), 1410.0),
    (2, date(2026, 9, 16), 1405.0),
    (2, date(2026, 9, 17), 1415.0),
    (2, date(2026, 9, 18), 1420.0),
    (3, date(2026, 9, 18), 1390.0),
    (4, date(2026, 9, 18), 1395.0),
]


def cargar_datos_iniciales(conexion: ConexionDB) -> None:
    """Reemplaza los datos de la base por el conjunto de ejemplo."""
    try:
        with conexion.transaccion() as sesion:
            _vaciar_tablas(sesion)
            sesion.add_all(
                ModeloGenero(id_genero=id, nombre=nombre)
                for id, nombre in enumerate(GENEROS, start=1)
            )
            sesion.add_all(
                ModeloEditorial(id_editorial=id, nombre=nombre)
                for id, nombre in enumerate(EDITORIALES, start=1)
            )
            sesion.add_all(
                ModeloMoneda(
                    id_moneda=id, codigo=codigo, descripcion=descripcion
                )
                for id, (codigo, descripcion) in enumerate(MONEDAS, start=1)
            )
            sesion.add_all(
                ModeloTipoCotizacion(
                    id_tipo_cotizacion=id, nombre=nombre
                )
                for id, nombre in enumerate(TIPOS_COTIZACION, start=1)
            )
            sesion.add_all(
                ModeloLibro(
                    id_libro=id,
                    isbn=isbn,
                    titulo=titulo,
                    autor=autor,
                    id_genero=genero_id,
                    id_editorial=editorial_id,
                )
                for id, (isbn, titulo, autor, genero_id, editorial_id) in
                enumerate(LIBROS, start=1)
            )
            sesion.add_all(
                ModeloPrecio(
                    id_precio=precio_id,
                    id_libro=libro_id,
                    monto=monto,
                    id_moneda=id_moneda,
                )
                for precio_id, (libro_id, monto, id_moneda) in
                _precios_iniciales()
            )
            sesion.add_all(
                ModeloStock(id_libro=libro_id, cantidad=cantidad)
                for libro_id, cantidad in STOCK
            )
            sesion.add_all(
                ModeloCotizacionDolar(
                    id_tipo_cotizacion=tipo_id, fecha=fecha, valor=valor
                )
                for tipo_id, fecha, valor in COTIZACIONES
            )
    except IntegrityError as error:
        raise ValueError(
            "No se pudieron cargar los datos iniciales por una "
            "restricción de integridad de la base de datos."
        ) from error


def _vaciar_tablas(sesion: Session) -> None:
    """Elimina datos en orden inverso a las dependencias foráneas."""
    for modelo in (
        ModeloCotizacionDolar,
        ModeloStock,
        ModeloPrecio,
        ModeloLibro,
        ModeloTipoCotizacion,
        ModeloMoneda,
        ModeloEditorial,
        ModeloGenero,
    ):
        sesion.execute(delete(modelo))


def _precios_iniciales() -> list[tuple[int, tuple[int, float, int]]]:
    """Asigna IDs estables a los dos precios iniciales de cada libro."""
    return [
        (precio_id, (libro_id, monto, id_moneda))
        for precio_id, (libro_id, monto, id_moneda) in enumerate(
            (
                (libro_id, monto, id_moneda)
                for libro_id, monto_ars, monto_usd in PRECIOS
                for monto, id_moneda in (
                    (monto_ars, 1),
                    (monto_usd, 2),
                )
            ),
            start=1,
        )
    ]
