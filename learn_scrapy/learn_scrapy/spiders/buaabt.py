# -*- coding: utf-8 -*-
import scrapy


class BuaabtSpider(scrapy.Spider):
    name = "buaabt"
    allowed_domains = ["buaabt.cn"]
    start_urls = ['http://buaabt.cn']

    ## start_requests是调用这个方法
    def make_requests_from_url(self, url):
        login_url = self.start_urls[0] + '/login.aspx'
        login_data = {'username':'965001147',
                      'password':'chenxu'}
        # post登录
        return scrapy.FormRequest(url=login_url,
                                  formdata=login_data,
                                  callback=self.parse)

    def parse(self, response):
        # =========================================================== #
        # 进入shell调试方法
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        # =========================================================== #
        pass
