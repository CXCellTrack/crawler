# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import DoubanItem


class DoubanSpider(CrawlSpider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['https://www.douban.com/group/haixiuzu/discussion?start=0']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'DOWNLOAD_DELAY': 0, # 豆瓣有反爬机制
        'COOKIES_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'learn_scrapy.middlewares.MyUAMiddleware': 543
        },
        'ITEM_PIPELINES': {
            # 'scrapy.pipelines.images.ImagesPipeline': 1,
            'learn_scrapy.pipelines.MyImagesPipeline': 1
        },
        'IMAGES_STORE': 'scrapy_images/douban', # 图片存储位置
        'IMAGES_THUMBS': {'small': (150, 150)}, # 缩略图格式
    }
    cur_page = 1
    MAX_page = 3
    rules = (
        ## 帖子连接
        Rule(LinkExtractor(allow=r'https://www.douban.com/group/topic/\d+/',
                           restrict_xpaths=u'//td[@class="title"]/a[starts-with(@title,"【晒】")]'),
             callback='parse_item'),
        ## 下页连接（不设callback，使之递归抓取）
        Rule(LinkExtractor(allow=r'.+',
                           restrict_xpaths=u'//div[@class="paginator"]//a[text()="后页>"]'),
             callback='parse'),
    )

    # =========================================================== #
    # 重写parse方法，控制递归深度（即页数）
    # =========================================================== #
    def parse(self, response):
        if self.cur_page>self.MAX_page:
            return
        self.logger.info('process page %s...' % self.cur_page)
        self.cur_page += 1
        return self._parse_response(response, self.parse_start_url, cb_kwargs={}, follow=True)

    # =========================================================== #
    # 处理每个帖子
    # =========================================================== #
    def parse_item(self, response):
        # =========================================================== #
        #  进入shell调试方法
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        # =========================================================== #
        item = DoubanItem()
        item['image_urls'] = []
        item['image_paths'] = []
        title = response.xpath('//div[@id="content"]/h1/text()').extract_first().strip()
        imglinks = response.xpath('//div[@class="topic-figure cc"]/img/@src').extract()
        item['title'] = title
        item['image_urls'].extend(imglinks)
        # 标题计数器
        title_path = self.valid_filename(title)
        item['image_paths'].extend(['%s-%s.jpg' % (title_path, i)
                                    for i in range(len(imglinks))])
        yield item

    @staticmethod
    def valid_filename(name):
        for ch in r'\/:*?"<>|':
            name = name.replace(ch, '_')
        return name
