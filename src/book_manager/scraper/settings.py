BOT_NAME = "book_manager"

SPIDER_MODULES = ["book_manager.scraper.spiders"]
NEWSPIDER_MODULE = "book_manager.scraper.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
    "book_manager.scraper.pipelines.ValidateBookPipeline": 100,
    "book_manager.scraper.pipelines.JsonLinesExportPipeline": 200,
}
