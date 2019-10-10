# -*- coding: utf-8 -*-
import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'docs'
    allowed_domains = ['docs.microsoft.com']
    start_urls = ['https://docs.microsoft.com/en-us/']

    def parse(self, response):
        NEXT_PAGE_SELECTOR = '.directory-cols li>a::attr(href)'
        next_page = (
            f'{href}toc.json'
            for href in response.css(NEXT_PAGE_SELECTOR).getall()
        )
        for page in next_page:
            yield scrapy.Request(
                response.urljoin(page),
                callback=self.parse_toc
            )

    def parse_toc(self, response):
        if response.status == 404:
            self.logger.error('fuck')
        self.logger.error(response.url)

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
