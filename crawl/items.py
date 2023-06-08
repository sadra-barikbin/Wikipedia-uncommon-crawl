# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Document(scrapy.Item):
    lang_code = scrapy.Field()
    lang_name = scrapy.Field()
    text = scrapy.Field()
