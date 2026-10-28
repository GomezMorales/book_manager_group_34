"""Funciones compartidas para validar coincidencias de títulos."""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Optional

UMBRAL_SIMILITUD_TITULO = 0.75
SUFIJOS_DE_EDICION = {
    "bolsillo",
    "edicion de bolsillo",
    "edicion especial",
    "edicion ilustrada",
    "edicion limitada",
    "rustica",
    "tapa blanda",
    "tapa dura",
}


def normalizar_titulo(titulo: str) -> str:
    """Normaliza mayúsculas, tildes y espacios de un título."""
    sin_tildes = unicodedata.normalize("NFKD", titulo)
    sin_tildes = "".join(
        caracter
        for caracter in sin_tildes
        if not unicodedata.combining(caracter)
    )
    sin_puntuacion = re.sub(r"[^\w\s]", " ", sin_tildes.lower())
    return " ".join(sin_puntuacion.split())


def similitud_titulos(
    titulo_catalogo: str, titulo_web: Optional[str]
) -> float:
    """Devuelve la similitud entre dos títulos, entre 0 y 1."""
    if not titulo_web:
        return 0.0
    catalogo = normalizar_titulo(titulo_catalogo)
    web = normalizar_titulo(titulo_web)
    numeros_catalogo = set(re.findall(r"\d+", catalogo))
    numeros_web = set(re.findall(r"\d+", web))
    if not numeros_catalogo.issubset(numeros_web):
        return 0.0
    if catalogo == web:
        return 1.0
    if (
        web.startswith(f"{catalogo} ")
        and web[len(catalogo) + 1:] in SUFIJOS_DE_EDICION
    ):
        return 0.9
    return SequenceMatcher(None, catalogo, web).ratio()


def es_coincidencia_valida(
    titulo_catalogo: str,
    titulo_web: Optional[str],
    umbral: float = UMBRAL_SIMILITUD_TITULO,
) -> bool:
    """Indica si el título web supera el mínimo de similitud."""
    return similitud_titulos(titulo_catalogo, titulo_web) >= umbral
