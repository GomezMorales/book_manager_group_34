
"""Loaders para limpiar los datos extraídos de Cúspide."""

import re

from itemloaders import ItemLoader
from itemloaders.processors import Join, MapCompose, TakeFirst

from book_manager.scraper.items import CuspideBookItem


def clean_text(value):
    """Normaliza espacios en un texto."""

    return " ".join(value.split()) if value else None


def parse_price(value):
    """Convierte precios argentinos a números decimales."""

    if value is None:
        return None

    # Conserva solamente dígitos, puntos y comas.
    numero = re.sub(r"[^\d,.]", "", str(value))

    if not numero:
        return None

    if "," in numero and "." in numero:
        # Ejemplo argentino: 21.800,00
        if numero.rfind(",") > numero.rfind("."):
            numero = numero.replace(".", "")
            numero = numero.replace(",", ".")
        else:
            # Ejemplo internacional: 21,800.00
            numero = numero.replace(",", "")

    elif "," in numero:
        decimales = len(numero.rsplit(",", 1)[1])

        if decimales in (1, 2):
            numero = numero.replace(".", "")
            numero = numero.replace(",", ".")
        else:
            numero = numero.replace(",", "")

    elif "." in numero:
        decimales = len(numero.rsplit(".", 1)[1])

        # 21.800 representa veintiún mil ochocientos.
        # 900.00 representa novecientos con dos decimales.
        if decimales not in (1, 2):
            numero = numero.replace(".", "")

    try:
        precio = float(numero)
    except ValueError:
        return None

    return precio if precio > 0 else None


def clean_payment_method(value):
    """Limpia el marcador de lista de los métodos de pago."""
    if not value:
        return None
    valor_limpio = re.sub(
        r"^(Argentina|Internacional):\s*>?\s*",
        r"\1: ",
        value,
    )
    return valor_limpio.lstrip("> ").strip()


class CuspideBookLoader(ItemLoader):
    """Limpia y estructura los datos de cada producto."""

    default_item_class = CuspideBookItem
    default_output_processor = TakeFirst()

    title_in = MapCompose(clean_text)
    catalog_title_in = MapCompose(clean_text)

    description_in = MapCompose(clean_text)
    description_out = Join(" ")

    payment_methods_in = MapCompose(clean_text, clean_payment_method)
    payment_methods_out = Join(" | ")

    price_in = MapCompose(parse_price)
