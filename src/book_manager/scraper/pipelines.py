import json
from pathlib import Path

from scrapy.exceptions import DropItem


class ValidateBookPipeline:
    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        if not item.get("product_url"):
            raise DropItem("Libro descartado: no tiene URL")

        if item.get("price") is None:
            raise DropItem("Libro descartado: no tiene precio")

        if item["product_url"] in self.seen_urls:
            raise DropItem("Libro descartado: URL duplicada")

        self.seen_urls.add(item["product_url"])
        return item


class JsonLinesExportPipeline:
    def open_spider(self, spider):
        output_dir = Path("scraper_output")
        output_dir.mkdir(exist_ok=True)

        self.file = (output_dir / "cuspide_books.jsonl").open(
            "w",
            encoding="utf-8",
        )

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(f"{line}\n")
        return item

    def close_spider(self, spider):
        self.file.close()
