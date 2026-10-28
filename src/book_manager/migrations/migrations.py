"""Migración de datos de los CSV del Sprint 1 a la base de datos relacional."""

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from book_manager.database.connection import ConexionDB
from book_manager.models.models import Base


def _literal_entero(valor: str) -> str:
    """Valida un entero y lo devuelve como literal SQL."""
    return str(int(valor))


def _literal_decimal(valor: str) -> str:
    """Valida un número decimal y lo devuelve como literal SQL."""
    try:
        return str(Decimal(valor))
    except InvalidOperation as error:
        raise ValueError(f"Valor decimal inválido: '{valor}'.") from error


def _literal_fecha(valor: str) -> str:
    """Valida una fecha ISO (AAAA-MM-DD) y la devuelve como literal SQL."""
    return f"'{date.fromisoformat(valor)}'"


def _literal_texto(valor: str) -> str:
    """Devuelve un texto como literal SQL, duplicando las comillas simples."""
    return "'" + valor.strip().replace("'", "''") + "'"


@dataclass(frozen=True)
class TablaMigracion:
    """Describe cómo migrar un archivo CSV a una tabla.

    Attributes:
        orden: Posición en la migración (respeta las claves foráneas).
        tabla: Nombre de la tabla destino.
        archivo_csv: Nombre del archivo CSV de origen.
        columnas: Columnas de la tabla, en el orden del CSV.
        conversores: Función que convierte cada valor del CSV en literal SQL.
        clave_serial: Columna autonumérica de la tabla, si la tiene.
    """

    orden: int
    tabla: str
    archivo_csv: str
    columnas: Tuple[str, ...]
    conversores: Tuple[Callable[[str], str], ...]
    clave_serial: Optional[str] = None

    @property
    def archivo_sql(self) -> str:
        """Nombre del archivo .sql que se genera para la tabla."""
        return f"{self.orden:02d}_{self.tabla}.sql"


# Orden: primero las tablas de las que dependen otras (claves foráneas).
TABLAS: Tuple[TablaMigracion, ...] = (
    TablaMigracion(
        1, "generos", "generos.csv",
        ("id_genero", "nombre"),
        (_literal_entero, _literal_texto),
        clave_serial="id_genero",
    ),
    TablaMigracion(
        2, "editoriales", "editoriales.csv",
        ("id_editorial", "nombre"),
        (_literal_entero, _literal_texto),
        clave_serial="id_editorial",
    ),
    TablaMigracion(
        3, "monedas", "monedas.csv",
        ("id_moneda", "codigo", "descripcion"),
        (_literal_entero, _literal_texto, _literal_texto),
        clave_serial="id_moneda",
    ),
    TablaMigracion(
        4, "tipos_cotizacion", "tipos_cotizacion.csv",
        ("id_tipo_cotizacion", "nombre"),
        (_literal_entero, _literal_texto),
        clave_serial="id_tipo_cotizacion",
    ),
    TablaMigracion(
        5, "libros", "libros.csv",
        ("id_libro", "isbn", "titulo", "autor", "id_genero", "id_editorial"),
        (
            _literal_entero, _literal_texto, _literal_texto,
            _literal_texto, _literal_entero, _literal_entero,
        ),
        clave_serial="id_libro",
    ),
    TablaMigracion(
        6, "precios", "precios.csv",
        ("id_precio", "id_libro", "monto", "id_moneda"),
        (
            _literal_entero, _literal_entero,
            _literal_decimal, _literal_entero,
        ),
        clave_serial="id_precio",
    ),
    TablaMigracion(
        7, "stock", "stock.csv",
        ("id_libro", "cantidad"),
        (_literal_entero, _literal_entero),
    ),
    TablaMigracion(
        8, "cotizaciones_dolar", "cotizaciones_dolar.csv",
        ("id_tipo_cotizacion", "fecha", "valor"),
        (_literal_entero, _literal_fecha, _literal_decimal),
    ),
)


def _leer_filas(ruta_csv: Path, cantidad_columnas: int) -> List[List[str]]:
    """Lee un CSV sin encabezado y valida la cantidad de columnas.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si alguna fila no tiene la cantidad esperada de columnas.
    """
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el archivo {ruta_csv}.")
    with open(ruta_csv, newline="", encoding="utf-8") as archivo:
        filas = [fila for fila in csv.reader(archivo) if fila]
    for numero, fila in enumerate(filas, start=1):
        if len(fila) != cantidad_columnas:
            raise ValueError(
                f"{ruta_csv.name}, fila {numero}: se esperaban "
                f"{cantidad_columnas} columnas y hay {len(fila)}."
            )
    return filas


def _generar_sentencias(
    tabla: TablaMigracion, filas: List[List[str]]
) -> List[str]:
    """Arma un INSERT por fila. ON CONFLICT permite repetir la migración."""
    columnas = ", ".join(tabla.columnas)
    sentencias: List[str] = []
    for fila in filas:
        valores = ", ".join(
            convertir(valor)
            for convertir, valor in zip(tabla.conversores, fila)
        )
        sentencias.append(
            f"INSERT INTO {tabla.tabla} ({columnas}) "
            f"VALUES ({valores}) ON CONFLICT DO NOTHING;"
        )
    return sentencias


def _escribir_sql(ruta_sql: Path, sentencias: List[str]) -> None:
    """Guarda las sentencias de una tabla en un archivo .sql."""
    ruta_sql.write_text("\n".join(sentencias) + "\n", encoding="utf-8")


def _ejecutar_sql(sesion: Session, ruta_sql: Path) -> None:
    """Ejecuta, una por una, las sentencias de un archivo .sql."""
    for linea in ruta_sql.read_text(encoding="utf-8").splitlines():
        sentencia = linea.strip()
        if sentencia:
            # "\:" evita que SQLAlchemy interprete ":" como un parámetro.
            sesion.execute(text(sentencia.replace(":", "\\:")))


def _reiniciar_secuencias(sesion: Session) -> None:
    """Alinea los contadores autonuméricos de PostgreSQL con los ids cargados.

    Los CSV traen ids explícitos, por lo que la secuencia queda atrasada y el
    próximo alta sin id fallaría por clave duplicada.
    """
    if sesion.get_bind().dialect.name != "postgresql":
        return
    for tabla in TABLAS:
        if tabla.clave_serial is None:
            continue
        clave = tabla.clave_serial
        sesion.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{tabla.tabla}', "
                f"'{clave}'), COALESCE(MAX({clave}), 1), "
                f"MAX({clave}) IS NOT NULL) FROM {tabla.tabla}"
            )
        )


def migrar_datos(
    carpeta_csvs: str,
    carpeta_sqls: str,
    conexion: Optional[ConexionDB] = None,
) -> None:
    """Función encargada de la migración de datos de csv a sql.

    Se encarga de leer los archivos csv y crear los archivos sql
    para la inserción en la base de datos.

    Crea las tablas si no existen, genera un archivo .sql por tabla y lo
    ejecuta dentro de una única transacción: si algo falla no se carga nada.
    Se puede ejecutar más de una vez sin duplicar datos.

    Args:
        carpeta_csvs (str): Carpeta donde se encuentran los archivos csv
            de origen.
        carpeta_sqls (str): Carpeta donde se deben guardar los archivos
            sql generados.
        conexion (Optional[ConexionDB]): Conexión a usar. Si no se indica,
            se crea una a partir del archivo .env.

    Raises:
        FileNotFoundError: Si falta alguno de los archivos csv.
        ValueError: Si algún csv tiene filas o valores inválidos.
    """
    ruta_csvs = Path(carpeta_csvs)
    ruta_sqls = Path(carpeta_sqls)
    ruta_sqls.mkdir(parents=True, exist_ok=True)

    # Se genera todo primero: si un csv es inválido, falla antes de tocar
    # la base de datos.
    archivos_sql: List[Tuple[TablaMigracion, Path, int]] = []
    for tabla in TABLAS:
        filas = _leer_filas(
            ruta_csvs / tabla.archivo_csv, len(tabla.columnas)
        )
        ruta_sql = ruta_sqls / tabla.archivo_sql
        _escribir_sql(ruta_sql, _generar_sentencias(tabla, filas))
        archivos_sql.append((tabla, ruta_sql, len(filas)))

    conexion_propia = conexion is None
    if conexion is None:
        conexion = ConexionDB()
    try:
        Base.metadata.create_all(conexion.engine)
        with conexion.transaccion() as sesion:
            for tabla, ruta_sql, cantidad in archivos_sql:
                _ejecutar_sql(sesion, ruta_sql)
                print(f"{tabla.tabla:<20} {cantidad:>3} filas -> "
                      f"{ruta_sql.name}")
            _reiniciar_secuencias(sesion)
    finally:
        if conexion_propia:
            conexion.cerrar()


def cargar_datos_desde_sql(
    carpeta_sqls: str,
    conexion: Optional[ConexionDB] = None,
) -> int:
    """Carga en la base de datos los datos de los archivos .sql existentes.

    Ejecuta los archivos generados por migrar_datos en orden de claves
    foráneas, dentro de una única transacción. Es repetible (ON CONFLICT).

    Args:
        carpeta_sqls (str): Carpeta donde están los archivos sql.
        conexion (Optional[ConexionDB]): Conexión a usar. Si no se indica,
            se crea una a partir del archivo .env.

    Returns:
        int: Cantidad de archivos sql ejecutados.

    Raises:
        FileNotFoundError: Si falta alguno de los archivos sql.
    """
    ruta_sqls = Path(carpeta_sqls)
    archivos_sql: List[Tuple[TablaMigracion, Path]] = []
    for tabla in TABLAS:
        ruta_sql = ruta_sqls / tabla.archivo_sql
        if not ruta_sql.exists():
            raise FileNotFoundError(f"No se encontró el archivo {ruta_sql}.")
        archivos_sql.append((tabla, ruta_sql))

    conexion_propia = conexion is None
    if conexion is None:
        conexion = ConexionDB()
    try:
        Base.metadata.create_all(conexion.engine)
        with conexion.transaccion() as sesion:
            for tabla, ruta_sql in archivos_sql:
                _ejecutar_sql(sesion, ruta_sql)
                contenido = ruta_sql.read_text(encoding="utf-8")
                cantidad = sum(
                    1 for linea in contenido.splitlines() if linea.strip()
                )
                print(
                    f"{tabla.tabla:<20} {cantidad:>3} sentencias "
                    f"<- {ruta_sql.name}"
                )
            _reiniciar_secuencias(sesion)
    finally:
        if conexion_propia:
            conexion.cerrar()
    return len(archivos_sql)
