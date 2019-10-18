# -*- coding: utf-8 -*-
import json
import urllib.parse as urlparse

import scrapy


class DocRootCrawler(scrapy.Spider):
    name = 'docs-root'
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
        url = urlparse.urljoin(url, 'toc.json')
        yield scrapy.Request(
            url,
            callback=self._parse_toc,
        )

    def _parse_toc(self, response):
        if response.status == 404:
            self.logger.warning(f'Bad URL resolved. Could not find TOC. {response.status} {response.url}')
        yield {
            'status': response.status,
            'url': response.url
        }


class TOCCrawler(scrapy.Spider):
    name = 'docs-toc'
    allowed_domains = ['docs.microsoft.com']

    def start_requests(self):
        with open('results/docs-root.json', 'r') as file:
            responses = json.load(file)
        good_urls = self._response_gen(responses)
        return [
            scrapy.Request(
                url,
                callback=self.parse_toc
            ) for url in good_urls
        ]

    def _response_gen(self, responses):
        for response in responses:
            if response['status'] == 200:
                yield response['url']

    def parse_toc(self, response):
        try:
            json_response = json.loads(response.body_as_unicode())
        except json.decoder.JSONDecodeError:
            self.logger.warning(f'Invalid JSON: {response.url}')
            return
        for item in json_response['items']:
            yield from self.resolve_toc(response, item)

    def resolve_toc(self, response, item):
        url = response.url.rstrip('toc.json')
        if item.get('tocHref'):
            yield scrapy.Request(
                urlparse.urljoin(url, item['tocHref']),
                callback=self.parse_toc
            )
        if item.get('href'):
            yield scrapy.Request(
                urlparse.urljoin(url, item['href']),
                callback=self.parse_doc,
            )
        if item.get('children'):
            for child in item['children']:
                yield from self.resolve_toc(response, child)

    def parse_doc(self, response):
        IMG_SELECTOR = 'img[data-linktype=relative-path]::attr(src)'
        imgs = response.css(IMG_SELECTOR).getall()
        for img in imgs:
            yield {
                'url': response.url,
                'img': response.urljoin(img),
            }
