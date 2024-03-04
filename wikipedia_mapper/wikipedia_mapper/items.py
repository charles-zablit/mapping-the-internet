# wikipedia_mapper/items.py

import scrapy


class WikipediaPage(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    links = scrapy.Field()
