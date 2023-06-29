import scrapy

class Document(scrapy.Item):
    lang_code = scrapy.Field()
    lang_name = scrapy.Field()
    text = scrapy.Field()

    def __repr__(self):
        return f"Language: {self['lang_code']}({self['lang_name']})\nText: \"{self['text'][:500]}\""