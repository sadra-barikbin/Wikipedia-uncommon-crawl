BOT_NAME = 'Wikipedia_uncommon_crawl'

SPIDER_MODULES = ['crawl.spiders']
NEWSPIDER_MODULE = 'crawl.spiders'

from crawl.items import Document

FEED_EXPORTERS = {
   'txt': 'crawl.exporters.DocumentExporter'
}

FEEDS = {
   'dummy.txt':{
      'format': 'txt',
      'encoding': 'utf8',
      'item_classes': [Document],
      'fields': 'text'
   }
}

USER_AGENT = 'Wikipedia Uncommon Crawl'

DOWNLOAD_DELAY = 0.5

COOKIES_ENABLED = False

REFERRER_POLICY = 'scrapy.spidermiddlewares.referer.NoReferrerPolicy'

DUPEFILTER_DEBUG = True