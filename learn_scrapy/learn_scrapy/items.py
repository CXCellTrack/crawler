# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DmozItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    sub_title = scrapy.Field()
    link = scrapy.Field()


class WeiboItem(scrapy.Item):
    pass


class BuaabtItem(scrapy.Item):
    pass
