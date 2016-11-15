# -*- coding: utf-8 -*-
import scrapy
from ..items import DmozItem


class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = ['http://www.dmoz.org']


    def parse(self, response):
        asides = response.xpath('//*[@id="category-section"]/aside')
        for sel in asides:
            sel = sel.xpath('div/h2/a')[0]
            title = sel.xpath('text()').extract_first()
            if title in ['Sports', 'Arts']:
                print 'process %s..' % title
                link = sel.xpath('@href').extract_first()
                full_link = response.urljoin(link)
                yield scrapy.Request(full_link, callback=self.parse_title)


    def parse_title(self, response):
        divs = response.xpath('//*[@id="cat-list-content-main"]/div')
        for sel in divs:
            item = DmozItem()
            item['link'] = sel.xpath('a/@href').extract_first()
            texts = map(lambda x: x.encode('utf-8').strip(), sel.xpath('a/div/text()').extract())
            item['sub_title'] = filter(lambda x: x, texts)[0].decode('utf-8')
            yield item




