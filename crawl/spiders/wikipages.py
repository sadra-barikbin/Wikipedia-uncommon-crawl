import re
import scrapy
from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import CloseSpider
from typing import Dict, Iterable, Union, List
from collections import defaultdict
from crawl.items import Document
from scrapy.linkextractors import LinkExtractor

LANG_SPLIT_PATTERN = re.compile(r'https?://|\.')
def extract_page_lang(url: str):
    try:
        return re.split(LANG_SPLIT_PATTERN, url)[1]
    except IndexError:
        return ""

class SameLanguageLinkExtractor(LinkExtractor):
    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = self.link_extractor._extract_links(selector, response_url, response_encoding, base_url)
        return filter(lambda link: extract_page_lang(link.url) == extract_page_lang(response_url), links)


class WikiPageSpider(scrapy.Spider):
    name = 'wiki_spider'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://meta.wikimedia.org/wiki/List_of_Wikipedias']
    
    link_extractor = SameLanguageLinkExtractor(
        allow="https://[a-z-]+\.wikipedia.org/wiki/",
        deny="https://[a-z-]+\.wikipedia.org/wiki/.+:.+",
        allow_domains="wikipedia.org",
        canonicalize=True,
        unique=True,
        restrict_xpaths="//div[@id='mw-content-text']"
    )

    lang_code_to_name: Dict[str, str]

    def __init__(
        self,
        seed_page_url: str = 'https://en.wikipedia.org/wiki/Human',
        num_top_languages: int= 80,
        include_languages: List[str]= [],
        exclude_languages: List[str]= [],
        limit_in_gb: int=0.001,
        limit_in_per_lang_article_count: int = 100,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.limit_in_mb = float(limit_in_gb) * 1024
        self.size_in_byte = 0

        self.limit_in_per_lang_article_count = limit_in_per_lang_article_count
        self.num_articles_per_lang: Dict[str, int] = defaultdict(lambda: 0)

        self.num_top_languages = num_top_languages
        self.include_languages = include_languages
        self.exclude_languages = exclude_languages

        self.seed_page_url = seed_page_url

    def parse(self, response: HtmlResponse) -> scrapy.Request:
        name_codes = response.css(".list-of-wikipedias-table").xpath("./tbody/tr/td[4]/a/text()").getall()
        names = response.css(".list-of-wikipedias-table").xpath("./tbody/tr/td[2]/a/text()").getall()
        indices = filter(lambda i: name_codes[i] not in self.exclude_languages, range(len(name_codes)))
        indices = filter(lambda i: name_codes[i] in self.include_languages or i < self.num_top_languages, indices)
        self.lang_code_to_name = {name_codes[i]: names[i] for i in indices}
        self.logger.info(f"Selected languages: {name_codes}")

        return scrapy.Request(self.seed_page_url, callback=self.parse_page_response, cb_kwargs={'is_seed': True})

    def parse_page_response(self, response: HtmlResponse, is_seed=False) -> Iterable[Union[scrapy.Request, Document]]:
        article = response.xpath("//div[@id='mw-content-text']")[0]
        
        lang_code = extract_page_lang(response.url)
        text = ''.join(article.css(".mw-parser-output").xpath("p | blockquote/p").xpath("./text()|./b/text()|./a/text()").getall())
        if len(text) > 0:
            self.size_in_byte += len(text.encode())
            if (self.size_in_byte >> 20) >= self.limit_in_mb:
                raise CloseSpider(f"Data size limit reached: {self.limit_in_mb / 1024}")

            self.num_articles_per_lang[lang_code] += 1

            yield Document(lang_code=lang_code, lang_name=self.lang_code_to_name[lang_code], text=text)

        if is_seed:
            page_lang_elements = response.css("li.interlanguage-link").xpath("a")
            yield from response.follow_all(
                filter(lambda a_selector: a_selector.attrib["lang"] in self.lang_code_to_name, page_lang_elements),
                callback=self.parse_page_response,
                priority= self.limit_in_per_lang_article_count
            )
        
        priority = self.limit_in_per_lang_article_count - self.num_articles_per_lang[lang_code]
        for link in self.link_extractor.extract_links(response):
            if self.num_articles_per_lang[lang_code] < self.limit_in_per_lang_article_count:
                yield scrapy.Request(link.url, callback=self.parse_page_response, priority=priority)
                priority -= 1
            else:
                break

