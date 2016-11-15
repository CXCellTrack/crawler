# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class WeiboSpider(CrawlSpider):
    name = "weibo"
    allowed_domains = ["weibo.cn"]
    start_urls = ['http://weibo.cn']
    my_cookies = "_T_WM=d6cab8dc7d2170c585ee1e9dbbb03940; ALF=1481710019; SCF=AtM3q-7zU0uhwItTp0WWnRdZH5dxcX9tTOboKf4-QLQV8J8Ox6leuaUUvgPQogwJr5w97S5GZFbqvMID6C0JByA.; SUB=_2A251Lcd_DeTxGedI6FIV9SrPwz-IHXVW0ek3rDV6PUNbktBeLRfskW2VE_5Naspu_t6QuQqTw9uzMFIanQ..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5VkKx12wC8CA3iA9K-w5oU5JpX5KMhUgL.Fo2ce05XSKB01he2dJLoIp9VdfvadJHkMcyaUgp.PciLPNUDMcHE; SUHB=0ft4ePXiieJP_x; SSOLoginState=1479128879"

    # =========================================================== #
    # 将document.cookies由字符串转换为dict/jsr
    # =========================================================== #
    def get_cookies(self):
        cookies_dict = {}
        for line in self.my_cookies.split(';'):
            # 其设置为1就会把字符串拆分成2份
            name, value = line.strip().split('=', 1)
            cookies_dict[name] = value
        return cookies_dict

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],
                             cookies=self.get_cookies(),
                             callback=self.parse)

    def parse(self, response):
        # =========================================================== #
        # 进入shell调试方法
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        # 通过对response的查看发现
        # =========================================================== #
        pass














