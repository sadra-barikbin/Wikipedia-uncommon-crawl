import re
import scrapy
import unidecode
from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import CloseSpider
from typing import Dict, Any, Iterable, Optional, Union, List
from collections import defaultdict
from crawl.items import Document
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class SameLanguageLinkExtractor(LinkExtractor):
    lang_split_pattern = re.compile(r'https?://|\.')
    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = self.link_extractor._extract_links(selector, response_url, response_encoding, base_url)
        response_lang_code = re.split(self.lang_split_pattern, response_url)[1]
        return filter(lambda link: re.split(self.lang_split_pattern, link.url)[1] == response_lang_code, links)


class WikiPageSpider(CrawlSpider):
    name = 'wiki_spider'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://meta.wikimedia.org/wiki/List_of_Wikipedias']
    rules = [
        Rule(
            SameLanguageLinkExtractor(
                allow="https://[a-z-]+\.wikipedia.org/wiki/",
                deny="https://[a-z-]+\.wikipedia.org/wiki/[A-Z][a-z]+:[A-za-z:_]+",
                allow_domains="wikipedia.org",
                canonicalize=True,
                unique=True
            ),
            callback="parse_page_response"
        )
    ]

    def __init__(
        self,
        seed_page_title: str = 'Human',
        num_top_languages: int= 80,
        include_languages: List[str]= [],
        exclude_languages: List[str]= [],
        limit_in_gb: int=0.001,
        limit_in_per_lang_article_count: int = 100,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.limit_in_mb = limit_in_gb * 1024
        self.limit_in_per_lang_article_count = limit_in_per_lang_article_count
        self.num_articles_per_lang: Dict[str, int] = defaultdict(lambda: 0)
        self.lang_code_to_name = {}
        self.num_top_languages = num_top_languages
        self.include_languages = include_languages
        self.exclude_languages = exclude_languages
        self.seed_page_title = seed_page_title

    def parse_start_url(self, response: HtmlResponse) -> Iterable[scrapy.Request]:
        wiki_pages = response.css(".list-of-wikipedias-table").xpath("./tbody/tr/td[4]/a/@href").getall()
        name_codes = response.css(".list-of-wikipedias-table").xpath("./tbody/tr/td[4]/a/text()").getall()
        names = response.css(".list-of-wikipedias-table").xpath("./tbody/tr/td[2]/a/text()").getall()
        indices = filter(lambda i: name_codes[i] not in self.exclude_languages, range(len(name_codes)))
        indices = filter(lambda i: name_codes[i] in self.include_languages or i < self.num_top_languages, indices)
        for i in indices:
            self.lang_code_to_name[name_codes[i]] = names[i]
            yield scrapy.Request(
                f"{wiki_pages[i]}{self.seed_page_title}",
                callback=self.parse_page_response,
            )

    def parse_page_response(self, response: HtmlResponse) -> Document:
        article = response.xpath("//div[@id='mw-content-text']")[0]
        lang_code = article.root.attrib['lang']
        excerpts = article.css(".mw-parser-output").xpath("p | blockquote/p").xpath("./text()|./b/text()|./a/text()")
        self.num_articles_per_lang[lang_code] += 1
        return Document(lang_code=lang_code, lang_name=self.lang_code_to_name[lang_code], text=''.join(excerpts))
