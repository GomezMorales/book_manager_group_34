import scrapy


class CuspideBookItem(scrapy.Item):
    catalog_title = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    image_url = scrapy.Field()
    payment_methods = scrapy.Field()
    description = scrapy.Field()
    product_url = scrapy.Field()
    scraped_at = scrapy.Field()
