# -*- coding: utf-8 -*-
import scrapy
import copy
import time
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ..items import WeiboItem


class WeiboSpider(CrawlSpider):
    name = "weibo"
    allowed_domains = ["weibo.cn"]
    start_urls = 'http://weibo.cn/'
    my_cookies = "_T_WM=d6cab8dc7d2170c585ee1e9dbbb03940; ALF=1481710019; SCF=AtM3q-7zU0uhwItTp0WWnRdZH5dxcX9tTOboKf4-QLQV8J8Ox6leuaUUvgPQogwJr5w97S5GZFbqvMID6C0JByA.; SUB=_2A251Lcd_DeTxGedI6FIV9SrPwz-IHXVW0ek3rDV6PUNbktBeLRfskW2VE_5Naspu_t6QuQqTw9uzMFIanQ..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5VkKx12wC8CA3iA9K-w5oU5JpX5KMhUgL.Fo2ce05XSKB01he2dJLoIp9VdfvadJHkMcyaUgp.PciLPNUDMcHE; SUHB=0ft4ePXiieJP_x; SSOLoginState=1479128879"

    MAX_PAGE = 5 # 最大爬取微博页数

    custom_settings = {
        'FILES_STORE': 'weibo_data',
        'ITEM_PIPELINES': {
            'learn_scrapy.pipelines.WeiboPipeline': 300,
            'learn_scrapy.pipelines.MyImagesPipeline': 10
        }
    }

    rules = (
        # 提取匹配'follow'和'fans'的链接并跟进链接(没有callback意味着follow默认为True)
        Rule(LinkExtractor(allow=('/\d+/follow', )), callback='parse_follow_and_fans'), # '/\d+/fans'
    )

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
        ## 使用cookies登录
        yield scrapy.Request(url=self.start_urls,
                             cookies=self.get_cookies())


    @staticmethod
    def get_user_name(td):
        isVip = td.xpath('img/@alt').extract_first()
        name = td.xpath('a[1]/text()').extract_first()
        return '%s-[V]' % name if isVip else name


    def parse_follow_and_fans(self, response):
        # =========================================================== #
        # 进入shell调试方法
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        # 通过对response的查看发现cookie登录成功
        # =========================================================== #
        tds = response.xpath('//body//table//td[@valign="top"][2]')
        for td in tds:
            ## 用户信息字典
            item = WeiboItem()
            item['name'] = self.get_user_name(td)
            item['user_info'] = {}
            item['weibo_info'] = {} # 微博内容
            item['file_urls'] = []

            link = td.xpath('a/@href').extract_first()
            ## 通过meta传递item # debug时先抓某一个人的
            if item['name'] not in [u'北娃大王-[V]', u'0木头-木头0']:
                continue
            yield scrapy.Request(url=link, callback=self.parse_user,
                                 meta={'item': item})
        ## 寻找下页链接
        pagelist = response.xpath('/html/body/div[@id="pagelist"]//a[1]')
        if pagelist and pagelist.xpath('text()').extract_first()==u'下页':
            np_link = pagelist.xpath('@href').extract_first()
            yield scrapy.Request(url=response.urljoin(np_link),
                                 callback=self.parse_follow_and_fans)


    # =========================================================== #
    # 爬取微博信息
    # =========================================================== #
    def parse_user(self, response):
        ## 在当前页面抓取简单信息
        info_link = self.parse_user_basic_info(response)
        ## 进入info页面抓取复杂信息
        yield scrapy.Request(url=response.urljoin(info_link),
                             callback=self.parse_user_verbose_info,
                             meta={'item': response.meta['item'],
                                   'home_url': response.url})
        ###### 注意：对于最后yield出去的函数，必须不能手动调用！要让scrapy系统自动调用！


    # =========================================================== #
    # 爬取微博信息1：个人信息
    # =========================================================== #
    def parse_user_basic_info(self, response):
        item = response.meta['item']
        ## 找到u'微博', u'关注', u'粉丝'信息
        uu = response.xpath('//body/div[@class="u"][1]')[0]
        wb_info = uu.xpath('div[@class="tip2"]')[0]
        texts = wb_info.xpath('.//text()')
        for fid in [u'微博', u'关注', u'粉丝']:
            item['user_info'][fid] = int(texts.re('%s\[(\d+)\]' % fid)[0])
        ## 找到个人详细信息（头像、简介等） # 对href的内容使用正则
        info_link = uu.xpath('.//div[@class="ut"]/a[re:test(@href, "/\d+/info")]/@href').extract_first()
        return info_link


    # =========================================================== #
    # 进入info页面抓取复杂信息
    # =========================================================== #
    def parse_user_verbose_info(self, response):
        item = response.meta['item']
        ## 得到头像地址
        headimg = response.xpath('//body/div[@class="c"][1]/img/@src').extract_first()
        item['user_info']['headimg'] = headimg
        item['file_urls'].append(headimg)
        ## 选择"基本信息""工作经历""其他信息"三个节点后的div
        infos = response.xpath(u'//body/div[@class="tip" and '
                               u'(text()="基本信息" or text()="工作经历" or text()="其他信息")]'
                               u'/following::div[1]')
        for i,info in enumerate(infos):
            ## 单独处理"工作经历"
            if i==1:
                item['user_info'].update({
                    u'工作经历': info.xpath('.//text()').extract_first()
                })
                continue
            ## 处理其他信息
            data = info.xpath('.//text()').re('.+:.+')
            item['user_info'].update(dict([x.split(':', 1) for x in data]))
        #### 确保抓完之后再抓每条微博（如果直接yield item，则抓取过程就结束）
        yield scrapy.Request(url=response.meta['home_url'],
                             callback=self.parse_user_weibo_info,
                             dont_filter=True, # 必须设为不过滤，因为url之前已经抓过
                             meta={'item': item,
                                   'cur_page': 1,
                                   'post_id': 0})


    # =========================================================== #
    # 爬取微博信息2：微博文字图片信息
    # =========================================================== #
    def parse_user_weibo_info(self, response):
        ## 给每条微博一个post_id
        post_id = response.meta['post_id']
        ## 找到每条微博
        posts = response.xpath('//body/div[@class="c" and @id]')
        for post in posts:
            ## 将item分发给每条微博
            item = copy.deepcopy(response.meta['item']) # 使用自带的copy()方法并非深复制
            post_id += 1
            print u'process %s ———— post %s...' % (item['name'], post_id)
            content = '\n'.join(post.xpath('./div[1]//text() | ./div[3]//text()').extract())
            imgs_link = post.xpath('./div[2]//a/img/parent::a/@href').extract_first()
            item['weibo_info'].update({'post_id': post_id,
                                       'content': content,
                                       'imgs_link': imgs_link})
            # 无图则返回item
            if not imgs_link:
                yield item
            else:
                yield scrapy.Request(url=imgs_link,
                                     callback=self.get_post_imgs,
                                     meta={'item': item})
        ## 翻页
        np_link = response.xpath(u'//div[@id="pagelist"]//a[text()="下页"]/@href').extract_first()
        cur_page = response.meta['cur_page']
        if np_link and cur_page<self.MAX_PAGE:
            yield scrapy.Request(url=response.urljoin(np_link),
                                 callback=self.parse_user_weibo_info,
                                 meta={'item': response.meta['item'],
                                       'cur_page': cur_page+1,
                                       'post_id': post_id+1})




    # =========================================================== #
    # 从每个帖子的图片链接获取帖子附图
    # =========================================================== #
    def get_post_imgs(self, response):
        item = response.meta['item']
        ## debug时限制帖子id
        # if response.meta['item']['weibo_info']['post_id']!=1:
        #     return
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        img_link = response.xpath('//body/div//img/@src').extract_first()
        ni_link = response.xpath(u'//body/div//a[text()="下一张"]/@href').extract_first()
        ## 图片加入下载库
        item['file_urls'].append(img_link) # 使用imagePipeline无法下载gif格式的！
        ## 获取下一张图片
        if not ni_link:
            yield item
        else:
            yield scrapy.Request(url=response.urljoin(ni_link),
                                 callback=self.get_post_imgs,
                                 meta={'item': item})








