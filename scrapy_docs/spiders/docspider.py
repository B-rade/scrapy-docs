# -*- coding: utf-8 -*-
import sqlite3

import scrapy
from tqdm import tqdm


class DocRootCrawler(scrapy.Spider):
    name = 'docs-root'
    allowed_domains = ['docs.microsoft.com']
    start_urls = ['https://docs.microsoft.com/_sitemaps/sitemapindex.xml']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy_docs.pipelines.StoreUrlPipeline': 100,
        }
    }

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
    name = 'whats-up-docs'
    allowed_domains = ['docs.microsoft.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy_docs.pipelines.StoreImagePipeline': 100,
            'scrapy_docs.pipelines.VisitUrlPipeline': 200,
        }
    }

    def __init__(self):
        self.count = 0

    def start_requests(self):
        self.count = self.get_count()
        urls = self._url_gen()
        return tqdm(
            (scrapy.Request(
                url[1],
                callback=self.parse_doc,
                meta={'id': url[0]}
            ) for url in urls),
            total=self.count
        )

    def get_count(self):
        db = self.settings.get('DB')
        con = sqlite3.connect(db)
        with con:
            c = con.cursor()
            c.execute("SELECT COUNT(id) FROM urls WHERE visited = 0")
            result = c.fetchone()[0]
        con.close()
        return result

    def _url_gen(self):
        db = self.settings.get('DB')
        con = sqlite3.connect(db)
        with con:
            c = con.cursor()
            c.execute("SELECT id, url FROM urls WHERE visited = 0")
            results = c.fetchall()
        con.close()
        return results

    # def _cursor_gen(self, c):
    #     while True:
    #         results = c.fetchmany(1000)
    #         if not results:
    #             break
    #         for result in results:
    #             yield result

    def parse_doc(self, response):
        IMG_SELECTOR = 'img[data-linktype=relative-path]::attr(src)'
        imgs = response.css(IMG_SELECTOR).getall()
        for img in tqdm(imgs):  # give the illusion of progress
            yield {
                'url': response.url,
                'img': response.urljoin(img),
            }
        yield {
            'visited_url': response.url,
            'id': response.meta['id'],
        }
