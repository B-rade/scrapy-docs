# -*- coding: utf-8 -*-
import scrapy
from tqdm import tqdm


class DocRootCrawler(scrapy.Spider):
    name = 'docs-root'
    allowed_domains = ['docs.microsoft.com']
    start_urls = ['https://docs.microsoft.com/_sitemaps/sitemapindex.xml']

    def parse(self, response):
        NEXT_PAGE_SELECTOR = '//loc/text()'
        response.selector.remove_namespaces()
        index_urls = response.xpath(NEXT_PAGE_SELECTOR).getall()
        for index_url in tqdm(index_urls):
            if self.should_parse(index_url):
                yield scrapy.Request(
                    index_url,
                    callback=self.parse_index
                )

    def parse_index(self, response):
        NEXT_PAGE_SELECTOR = '//loc/text()'
        response.selector.remove_namespaces()
        urls = response.xpath(NEXT_PAGE_SELECTOR).getall()
        for url in tqdm(urls):
            if self.should_parse(url):
                yield {'url': url}

    def should_parse(self, url):
        return all([
            'en-us' in url,  # only parse english docs
            '/api/' not in url,  # don't parse api docs
            ]
        )


class DocCrawler(scrapy.Spider):
    name = 'docs-docs'
    allowed_domains = ['docs.microsoft.com']

    def start_requests(self):
        urls = self._url_gen()
        urls = (x['url'] for x in urls)
        return (
            scrapy.Request(
                url,
                callback=self.parse_doc
            ) for url in urls
        )

    def _url_gen(self):
        with open('results/docs-root.json', 'r') as file:
            yield from file

    def parse_doc(self, response):
        IMG_SELECTOR = 'img[data-linktype=relative-path]::attr(src)'
        imgs = response.css(IMG_SELECTOR).getall()
        for img in imgs:
            yield {
                'url': response.url,
                'img': response.urljoin(img),
            }
