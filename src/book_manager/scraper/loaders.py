import re
from itemloaders import ItemLoader
from itemloaders.processors import Join, MapCompose, TakeFirst

from book_manager.scraper.items import CuspideBookItem


def clean_text(value):
    return " ".join(value.split()) if value else None


def parse_price(value):
    if not value:
        return None

    cleaned = re.sub(r"[^\d,\.]", "", value).replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


class CuspideBookLoader(ItemLoader):
    default_item_class = CuspideBookItem
    default_output_processor = TakeFirst()

    title_in = MapCompose(clean_text)
    catalog_title_in = MapCompose(clean_text)
    description_in = MapCompose(clean_text)
    description_out = Join(" ")
    payment_methods_in = MapCompose(clean_text)
    payment_methods_out = Join(" | ")
    price_in = MapCompose(parse_price)
