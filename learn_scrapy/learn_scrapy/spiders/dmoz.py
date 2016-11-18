# -*- coding: utf-8 -*-
import scrapy
from ..items import DmozItem


class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = ['http://www.dmoz.org']

    custom_settings = {'ITEM_PIPELINES': {'learn_scrapy.pipelines.DmozPipeline': 300}}


    def parse(self, response):
        asides = response.xpath('//*[@id="category-section"]/aside')
        for sel in asides:
            sel = sel.xpath('div/h2/a')[0]
            title = sel.xpath('text()').extract_first()
            if title in ['Sports', 'Arts']:
                print 'process %s..' % title
                link = sel.xpath('@href').extract_first()
                full_link = response.urljoin(link)
                # 设定数据，通过meta传递数据
                item = DmozItem()
                item['title'] = title
                item['content'] = []
                yield scrapy.Request(full_link, callback=self.parse_title, meta={'item': item})


    def parse_title(self, response):
        divs = response.xpath('//*[@id="cat-list-content-main"]/div')
        item = response.meta['item']
        for sel in divs:
            link = sel.xpath('a/@href').extract_first()
            texts = map(lambda x: x.encode('utf-8').strip(), sel.xpath('a/div/text()').extract())
            sub_title = filter(lambda x: x, texts)[0].decode('utf-8')
            item['content'].append({'link':link, 'sub_title':sub_title})
        yield item




