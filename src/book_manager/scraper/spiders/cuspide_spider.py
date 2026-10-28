from datetime import datetime, timezone
from urllib.parse import quote_plus
import scrapy
from book_manager.scraper.loaders import CuspideBookLoader

class CuspideSpider(scrapy.Spider):
    name = "cuspide"
    allowed_domains = ["cuspide.com"]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    def __init__(self, book_titles=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not book_titles:
            raise ValueError(
                "Debés indicar títulos con: -a 'book_titles=Titulo 1|Titulo 2'"
            )
        self.book_titles = [
            title.strip()
            for title in book_titles.split("|")
            if title.strip()
        ]

    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/',
        }
        for title in self.book_titles:
            consulta = quote_plus(title)
            url = f"https://www.cuspide.com/Resultados.aspx?c={consulta}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_search,
                headers=headers,
                meta={"catalog_title": title},
            )

    def parse_search(self, response):
        links = response.css(
            "a[href*='Libro-']::attr(href), "
            "a[href*='libro-']::attr(href)"
        ).getall()

        unique_links = list(
            dict.fromkeys(response.urljoin(link) for link in links)
        )[:10]

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': response.url
        }

        for product_url in unique_links:
            yield response.follow(
                product_url,
                callback=self.parse_book,
                headers=headers,
                meta={"catalog_title": response.meta["catalog_title"]},
            )

    def parse_book(self, response):
        loader = CuspideBookLoader(response=response)
        loader.add_value("catalog_title", response.meta["catalog_title"])
        loader.add_css("title", "h1::text")
        loader.add_css(
            "price",
            ".precio::text, .product-price::text, [class*='precio']::text, .item-price::text",
        )
        loader.add_css(
            "image_url",
            ".product-image img::attr(src), "
            ".imagen-producto img::attr(src), "
            "img::attr(src)",
        )
        loader.add_css(
            "payment_methods",
            "[class*='pago']::text, [class*='payment']::text, .formas-pago::text",
        )
        loader.add_css(
            "description",
            ".descripcion ::text, "
            ".description ::text, "
            "[class*='descripcion'] ::text",
        )
        loader.add_value("product_url", response.url)
        loader.add_value(
            "scraped_at",
            datetime.now(timezone.utc).isoformat(),
        )
        yield loader.load_item()
