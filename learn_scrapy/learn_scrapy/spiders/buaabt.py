# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader

from ..items import BuaabtItem


class BuaabtSpider(scrapy.Spider):
    name = "buaabt"
    allowed_domains = ["buaabt.cn"]
    start_urls = 'http://buaabt.cn/'
    custom_settings = {
        'IMAGES_STORE':'buaa_images',
        'ITEM_PIPELINES':{
            'learn_scrapy.pipelines.BuaabtPipeline':300,
            'learn_scrapy.pipelines.MyImagesPipeline':10
        }
    }
    max_page = 1

    ## 覆盖其中的start_requests方法
    def start_requests(self):
        login_url = self.start_urls + 'login.aspx'
        login_data = {'username':'965001147',
                      'password':'chenxu'}
        # post登录
        yield scrapy.FormRequest(url=login_url,
                                 formdata=login_data,
                                 callback=self.parse_forum)

    # =========================================================== #
    # 从主页解析出论坛地址
    # =========================================================== #
    def parse_forum(self, response):
        # =========================================================== #
        # 进入shell调试方法
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        # =========================================================== #
        for sel in response.xpath('//div[@id="category_1"]/table/tbody/tr/th/h2/a'):
            link = sel.xpath('@href').extract_first()
            forum = sel.xpath('span/text()').extract_first()
            if forum not in [u'品茶亭', u'跳蚤市场']:
                continue
            yield scrapy.Request(url=response.urljoin(link),
                                 callback=lambda r, f=forum, p=1:self.parse_post(r, f, p))

    # =========================================================== #
    # 从各论坛中解析出帖子地址
    # =========================================================== #
    def parse_post(self, response, forum, page):
        subjects = response.xpath('//table[@id="threadlist"]/tbody/tr/th[@class="subject"]/a')
        for sub in subjects:
            postlink = sub.xpath('@href').extract_first()
            postname = sub.xpath('.//text()').extract_first()
            # if postname not in [u'[新增视频了哦~~~如果你不知道她的真实年龄：猜猜她多大了][42P]']:
            #     continue
            yield scrapy.Request(url=response.urljoin(postlink),
                                 callback=lambda r, f=forum, n=postname:self.parse_image(r, f, n))
        ## 一页解析完毕需要翻页
        if page >= self.max_page:
            return
        page += 1
        nextpage_link = response.url[:-5] + '-%s.aspx' % page
        yield scrapy.Request(url=nextpage_link,
                             callback=lambda r, f=forum, p=page:self.parse_post(r, f, p))

    # =========================================================== #
    # 从帖子中解析图片地址
    # =========================================================== #
    def parse_image(self, response, forum, postname):
        ## 获取1楼的图片
        lz_imgs = response.xpath('//td[@class="postcontent"][1]//img[@imageid]')
        item = BuaabtItem()
        item['forum'] = forum
        item['postname'] = self.get_valid_filename(postname)
        item['file_urls'] = [] # 注意image_urls为数组
        for img in lz_imgs:
            img_link = img.xpath('@src').extract_first()
            item['file_urls'].append(response.urljoin(img_link))
        yield item

    @staticmethod
    def get_valid_filename(name):
        for ch in r'\/:*?"<>|.':
            name = name.replace(ch, '_')
        return name
