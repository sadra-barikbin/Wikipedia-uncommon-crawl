import scrapy

class Document(scrapy.Item):
    lang_code = scrapy.Field()
    lang_name = scrapy.Field()
    text = scrapy.Field()
