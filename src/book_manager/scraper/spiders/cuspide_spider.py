
"""Spider para obtener libros y precios desde Cúspide."""

from datetime import datetime, timezone
from urllib.parse import quote_plus, urlparse

import scrapy

from book_manager.scraper.loaders import CuspideBookLoader


class CuspideSpider(scrapy.Spider):
    """Busca productos en Cúspide y extrae sus datos."""

    name = "cuspide"
    allowed_domains = ["cuspide.com", "www.cuspide.com"]

    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 2,
    }

    def __init__(self, book_titles=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not book_titles:
            raise ValueError(
                "Debés indicar títulos con el argumento "
                "book_titles=Titulo 1|Titulo 2."
            )

        self.book_titles = [
            titulo.strip()
            for titulo in book_titles.split("|")
            if titulo.strip()
        ]

    def start_requests(self):
        """Inicia una búsqueda por cada título del catálogo."""

        headers = {
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/",
        }

        for titulo in self.book_titles:
            consulta = quote_plus(titulo)

            # Búsqueda de productos de WordPress / WooCommerce.
            url = (
                "https://cuspide.com/"
                f"?s={consulta}&post_type=product"
            )

            yield scrapy.Request(
                url=url,
                callback=self.parse_search,
                errback=self.request_failed,
                headers=headers,
                meta={"catalog_title": titulo},
            )

    def parse_search(self, response):
        """Extrae los enlaces a los productos encontrados."""

        titulo_catalogo = response.meta["catalog_title"]

        enlaces = response.css(
            'a[href*="/producto/"]::attr(href)'
        ).getall()

        enlaces_unicos = []

        for enlace in enlaces:
            url_producto = response.urljoin(enlace)
            ruta = urlparse(url_producto).path.lower()
            segmentos = [
                parte
                for parte in ruta.split("/")
                if parte
            ]

            # Acepta rutas /producto/nombre-del-libro/.
            if (
                len(segmentos) >= 2
                and segmentos[0] == "producto"
                and url_producto not in enlaces_unicos
            ):
                enlaces_unicos.append(url_producto)

            if len(enlaces_unicos) >= 10:
                break

        if not enlaces_unicos:
            self.logger.warning(
                "No se encontraron enlaces de productos para "
                "'%s'. URL de búsqueda: %s. HTTP: %s",
                titulo_catalogo,
                response.url,
                response.status,
            )
            return

        self.logger.info(
            "Se encontraron %s enlaces para '%s'.",
            len(enlaces_unicos),
            titulo_catalogo,
        )

        headers = {
            "Accept": "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Referer": response.url,
        }

        for url_producto in enlaces_unicos:
            yield scrapy.Request(
                url=url_producto,
                callback=self.parse_book,
                errback=self.request_failed,
                headers=headers,
                meta={"catalog_title": titulo_catalogo},
                # La misma URL puede corresponder a búsquedas distintas.
                dont_filter=True,
            )

    def parse_book(self, response):
        """Extrae el título, el precio y los datos de un producto."""

        titulo_catalogo = response.meta["catalog_title"]

        loader = CuspideBookLoader(response=response)

        loader.add_value("catalog_title", titulo_catalogo)

        # Selector principal y alternativa para el título.
        loader.add_css("title", "h1.product_title::text")
        loader.add_css("title", "h1::text")

        # Se priorizan los precios de venta de WooCommerce.
        # Si no están disponibles, se prueban selectores alternativos.
        selectores_precio = [
            (
                ".summary .price ins "
                ".woocommerce-Price-amount bdi::text"
            ),
            (
                ".summary .price ins "
                ".woocommerce-Price-amount::text"
            ),
            (
                ".summary .price "
                ".woocommerce-Price-amount bdi::text"
            ),
            (
                "p.price .woocommerce-Price-amount bdi::text"
            ),
            (
                ".price .woocommerce-Price-amount bdi::text"
            ),
            (".summary .price::text"),
            (".product-price::text"),
            (".precio::text"),
            ("[class*='precio']::text"),
        ]

        for selector in selectores_precio:
            loader.add_css("price", selector)

        loader.add_css(
            "image_url",
            ".woocommerce-product-gallery img::attr(src), "
            "img.wp-post-image::attr(src)",
        )

        loader.add_css(
            "description",
            ".woocommerce-product-details__short-description ::text, "
            ".woocommerce-Tabs-panel--description ::text, "
            ".descripcion ::text",
        )

        loader.add_value("product_url", response.url)

        loader.add_value(
            "scraped_at",
            datetime.now(timezone.utc).isoformat(),
        )

        item = loader.load_item()

        if not item.get("price"):
            self.logger.warning(
                "No se pudo extraer un precio para '%s'. "
                "Producto: %s",
                titulo_catalogo,
                response.url,
            )

        yield item

    def request_failed(self, failure):
        """Registra los errores de las solicitudes HTTP."""

        self.logger.error(
            "Falló una petición a Cúspide: %s",
            failure.getErrorMessage(),
        )
