
"""Validación y exportación de productos extraídos."""

import json
from pathlib import Path

from scrapy.exceptions import DropItem


class ValidateBookPipeline:
    """Descarta productos inválidos y evita duplicados."""

    def open_spider(self, spider=None):
        self.seen_keys = set()

    def process_item(self, item, spider=None):
        if not item.get("product_url"):
            raise DropItem("Libro descartado: no tiene URL.")

        try:
            precio = float(item.get("price"))
        except (TypeError, ValueError):
            raise DropItem(
                "Libro descartado: no tiene un precio válido."
            )

        if precio <= 0:
            raise DropItem(
                "Libro descartado: el precio debe ser mayor a cero."
            )

        item["price"] = precio

        # Una misma URL puede aparecer en la búsqueda de dos títulos.
        # La deduplicación se hace por título buscado y URL.
        clave = (
            item.get("catalog_title"),
            item.get("product_url"),
        )

        if clave in self.seen_keys:
            raise DropItem("Libro descartado: resultado duplicado.")

        self.seen_keys.add(clave)

        return item


class JsonLinesExportPipeline:
    """Guarda los productos válidos en formato JSON Lines."""

    def open_spider(self, spider=None):
        output_dir = Path("scraper_output")
        output_dir.mkdir(parents=True, exist_ok=True)

        self.file = (
            output_dir / "cuspide_books.jsonl"
        ).open("w", encoding="utf-8")

    def process_item(self, item, spider=None):
        linea = json.dumps(
            dict(item),
            ensure_ascii=False,
        )

        self.file.write(linea + "\n")

        return item

    def close_spider(self, spider=None):
        self.file.close()
