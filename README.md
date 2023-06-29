# Wikipedia Uncommon Crawl :)


## How to use

```
scrapy crawl wiki_spider [-a seed_page_url=<str>]
                         [-a num_top_languages=<int>]
                         [-a include_languages=<str> | "<str>, <str>, ..."]
                         [-a exclude_languages=<str> | "<str>, <str>, ..."]
                         [-a limit_in_gb=<float>]
                         [-a limit_in_per_lang_article_count=<int>]
```

Crawler arguments:
- **seed_page_url** The article link that crawl is started by. (Default: `'https://en.wikipedia.org/wiki/Human'`)
- **num_top_languages** Number of languages that have the most number of articles in Wikipedia. (default: 80)
- **include_languages** The languages that their articles must get collected.
- **exclude_languages** The languages that their articles must not get collected.
- **limit_in_gb** To limit the size of the collected data. (Default: 0.001 i.e. 1 MB)
- **limit_in_per_lang_article_count** To limit the number of articles collected per language. (Default: 100)

Crawler starts by `seed_page_url` and greedily follows the links within the articles to find new articles. It stops if either no link is left or any of the limits is met. Articles are written in separate files in their respective language folders under a folder named `wikidata` in the project root.

The crawler is written using Scrapy.