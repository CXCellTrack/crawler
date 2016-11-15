# -*- coding: utf-8 -*-
import scrapy
from learn_scrapy.items import LearnScrapyItem


class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = ['http://www.dmoz.org']

    





    def parse_title(self, response):
        for sel in response.xpath('//*[@id="main-nav"]/ul/li'):
            item = LearnScrapyItem()
            item['link'] = sel.xpath('a/@href').extract()[0].strip()
            item['desc'] = sel.xpath('a/text()').extract()[0].strip()
            yield item

