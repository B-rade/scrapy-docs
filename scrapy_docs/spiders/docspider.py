# -*- coding: utf-8 -*-
import scrapy


class DocRootCrawler(scrapy.Spider):
    name = 'docs'
    allowed_domains = ['docs.microsoft.com']
    start_urls = ['https://docs.microsoft.com/en-us/']

    def parse(self, response):
        NEXT_PAGE_SELECTOR = '.directory-cols li>a::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).getall()
        for page in next_page:
            yield scrapy.Request(
                response.urljoin(page),
                callback=self.parse_toc
            )

    def parse_toc(self, response):
        if response.url.endswith('index'):
            url = response.url.rstrip('index')
        else:
            url = response.url
        url += 'toc.json'
        yield scrapy.Request(
            url,
            callback=self._parse_toc,
        )

    def _parse_toc(self, response):
        if response.status == 404:
            self.logger.warning(f'{response.status} {response.url}')
        yield {
            'status': response.status,
            'url': response.url
        }


class TOCCrawler(scrapy.Spider):
    def parse_page(self, response):
        NEXT_PAGE_SELECTOR = 'a[data-linktype=absolute-path]::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).getall()
        for page in next_page:
            self.logger.info(page)
            yield scrapy.Request(
                response.urljoin(page),
                callback=self.parse_doc
            )

    def parse_doc(self, response):
        IMG_SELECTOR = 'img[data-linktype=relative-path]::attr(src)'
        imgs = response.css(IMG_SELECTOR).getall()
        for img in imgs:
            yield {
                'url': response.url,
                'img': response.urljoin(img),
            }
