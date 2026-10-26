"""Comparación de precios internos contra Cúspide y generación de alertas."""

import csv
import json
import os
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

from openpyxl import Workbook
from openpyxl.styles import Font

from book_manager.services.auditoria import auditar_metodos_publicos
from book_manager.services.services import ServicioPrecio

RAIZ_SRC = Path(__file__).resolve().parents[2]
RUTA_JSONL = RAIZ_SRC / "scraper_output" / "cuspide_books.jsonl"
CARPETA_REPORTES = Path(__file__).resolve().parents[1] / "reportes"
CODIGO_MONEDA_INTERNA = "ARS"
COLUMNAS_CSV = (
    "libro", "titulo_web", "precio_interno", "precio_web",
    "diferencia", "diferencia_porcentual", "url", "fecha_extraccion",
)


@dataclass
class AlertaPrecio:
    """Diferencia de precio de un libro que supera el umbral indicado."""

    libro: str
    titulo_web: str
    precio_interno: float
    precio_web: float
    diferencia: float
    diferencia_porcentual: float
    url: str
    fecha_extraccion: str


def _normalizar(texto: str) -> str:
    """Pasa a minúsculas y quita tildes para comparar títulos."""
    sin_tildes = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return " ".join(sin_tildes.lower().split())


def _similitud(titulo_catalogo: str, titulo_web: Optional[str]) -> float:
    """Devuelve qué tan parecidos son dos títulos (0 a 1)."""
    if not titulo_web:
        return 0.0
    a, b = _normalizar(titulo_catalogo), _normalizar(titulo_web)
    if a == b:
        return 1.0
    if a in b:
        return 0.9
    return SequenceMatcher(None, a, b).ratio()


def leer_resultados(ruta_jsonl: Path = RUTA_JSONL) -> List[dict]:
    """Lee los libros exportados por el scraper (un JSON por línea).

    Raises:
        FileNotFoundError: Si el scraper no generó el archivo.
    """
    if not ruta_jsonl.exists():
        raise FileNotFoundError(f"No se encontró {ruta_jsonl}.")
    with open(ruta_jsonl, encoding="utf-8") as archivo:
        return [json.loads(linea) for linea in archivo if linea.strip()]


def comparar_precios(
    resultados: List[dict],
    precios_internos: Dict[str, float],
    umbral: float,
) -> List[AlertaPrecio]:
    """Compara cada libro del catálogo con su mejor resultado en la web.

    Por cada título se elige el resultado más parecido entre los obtenidos
    y se genera una alerta si la diferencia porcentual supera el umbral.

    Args:
        resultados: Ítems del scraper (catalog_title, title, price, ...).
        precios_internos: Precio interno por título del catálogo.
        umbral: Diferencia porcentual mínima para alertar.

    Returns:
        List[AlertaPrecio]: Alertas ordenadas de mayor a menor diferencia.
    """
    alertas: List[AlertaPrecio] = []
    for titulo, precio_interno in precios_internos.items():
        candidatos = [
            r for r in resultados
            if r.get("catalog_title") == titulo and r.get("price")
        ]
        if not candidatos:
            continue
        mejor = max(
            candidatos, key=lambda r: _similitud(titulo, r.get("title"))
        )
        precio_web = float(mejor["price"])
        diferencia = precio_web - precio_interno
        porcentaje = diferencia / precio_interno * 100
        if abs(porcentaje) >= umbral:
            alertas.append(AlertaPrecio(
                libro=titulo,
                titulo_web=mejor.get("title") or "",
                precio_interno=round(precio_interno, 2),
                precio_web=round(precio_web, 2),
                diferencia=round(diferencia, 2),
                diferencia_porcentual=round(porcentaje, 2),
                url=mejor.get("product_url") or "",
                fecha_extraccion=mejor.get("scraped_at") or "",
            ))
    alertas.sort(key=lambda a: abs(a.diferencia_porcentual), reverse=True)
    return alertas


def generar_csv_alertas(
    alertas: List[AlertaPrecio],
    carpeta: Path = CARPETA_REPORTES,
) -> Path:
    """Guarda las alertas en un CSV nuevo con fecha y hora en el nombre.

    Se genera siempre, aunque no haya alertas (queda solo la cabecera).

    Returns:
        Path: Ruta del archivo generado.
    """
    carpeta.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = carpeta / f"alertas_{marca}.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS_CSV)
        escritor.writeheader()
        escritor.writerows(asdict(alerta) for alerta in alertas)
    return ruta


def generar_reporte_excel(
    alertas: List[AlertaPrecio],
    carpeta: Path = CARPETA_REPORTES,
) -> Path:
    """Exporta las comparaciones de precios a una nueva planilla Excel."""
    carpeta.mkdir(parents=True, exist_ok=True)
    libro_excel = Workbook()
    hoja = libro_excel.active
    hoja.title = "Comparación de precios"
    hoja.append(
        [
            "Libro",
            "Precio interno",
            "Precio web",
            "Diferencia",
            "Fecha de extracción",
        ]
    )
    for celda in hoja[1]:
        celda.font = Font(bold=True)

    for alerta in alertas:
        hoja.append(
            [
                alerta.libro,
                alerta.precio_interno,
                alerta.precio_web,
                alerta.diferencia,
                alerta.fecha_extraccion,
            ]
        )

    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions
    for columna in hoja.columns:
        ancho = max(len(str(celda.value or "")) for celda in columna)
        hoja.column_dimensions[columna[0].column_letter].width = min(
            ancho + 2, 60
        )

    marca = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    ruta = carpeta / f"comparacion_precios_{marca}.xlsx"
    libro_excel.save(ruta)
    return ruta


@dataclass
class ResultadoAlertas:
    """Resultado de una ejecución: alertas encontradas y CSV generado."""

    alertas: List[AlertaPrecio]
    ruta_csv: Path


@auditar_metodos_publicos
class ServicioAlertasPrecio:
    """Ejecuta el scraper y genera el CSV de alertas de precios."""

    def __init__(self, servicio_precio: ServicioPrecio) -> None:
        self._servicio_precio = servicio_precio

    def precios_internos(self) -> Dict[str, float]:
        """Devuelve el precio en pesos de cada libro del catálogo."""
        return {
            precio.libro.titulo: precio.monto
            for precio in self._servicio_precio.listar()
            if precio.moneda.codigo == CODIGO_MONEDA_INTERNA
        }

    @staticmethod
    def ejecutar_scraper(titulos: List[str]) -> Path:
        """Corre CuspideSpider con los títulos indicados.

        Se ejecuta en un proceso aparte porque Scrapy no permite
        reiniciar su motor dentro del mismo programa.

        Raises:
            RuntimeError: Si el scraper termina con error.
        """
        entorno = {**os.environ, "PYTHONPATH": str(RAIZ_SRC)}
        comando = [
            sys.executable, "-m", "scrapy", "crawl", "cuspide",
            "-a", f"book_titles={'|'.join(titulos)}",
        ]
        resultado = subprocess.run(
            comando, cwd=RAIZ_SRC, env=entorno,
            capture_output=True, text=True,
        )
        if resultado.returncode != 0:
            raise RuntimeError(
                f"El scraper falló:\n{resultado.stderr[-1500:]}"
            )
        return RUTA_JSONL

    def generar_alertas(
        self, umbral: float, scrapear: bool = True
    ) -> ResultadoAlertas:
        """Scrapea (opcional), compara precios y genera el CSV de alertas.

        Args:
            umbral: Diferencia porcentual mínima para alertar, indicada
                por el usuario antes de cada ejecución del scraper.
            scrapear: En False usa el último resultado del scraper.

        Returns:
            ResultadoAlertas: Alertas generadas y ruta del CSV.

        Raises:
            ValueError: Si el umbral es negativo.
            RuntimeError: Si el scraper termina con error.
        """
        if umbral < 0:
            raise ValueError("El umbral no puede ser negativo.")
        precios = self.precios_internos()
        if scrapear:
            self.ejecutar_scraper(list(precios))
        alertas = comparar_precios(leer_resultados(), precios, umbral)
        return ResultadoAlertas(alertas, generar_csv_alertas(alertas))

    def generar_reporte_excel(self, scrapear: bool = True) -> Path:
        """Genera Excel con todos los libros que tienen una coincidencia web."""
        precios = self.precios_internos()
        if not precios:
            raise ValueError(
                "No hay precios internos en ARS para generar el reporte."
            )
        if scrapear:
            self.ejecutar_scraper(list(precios))
        comparaciones = comparar_precios(
            leer_resultados(), precios, umbral=0
        )
        return generar_reporte_excel(comparaciones)
