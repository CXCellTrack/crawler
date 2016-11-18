# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DmozItem(scrapy.Item):
    # define the fields for your item here like:
    spider = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()


class WeiboItem(scrapy.Item):
    name = scrapy.Field() # 姓名
    user_info = scrapy.Field() # 基本资料 # 微博总数 # 粉丝数 # 关注数
    weibo_info = scrapy.Field() # 微博信息
    # 保存图片
    file_urls = scrapy.Field()
    files = scrapy.Field()
    image_datas = scrapy.Field()


class BuaabtItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()
    forum = scrapy.Field()
    postname = scrapy.Field()


