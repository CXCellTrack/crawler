# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:12:31 2016

@author: Administrator
"""

from scrapy import cmdline 


crawl_name = 'weibo'
DEBUG = 0
if DEBUG:
    cmd = 'scrapy crawl %s -L DEBUG -o test.json' % crawl_name
else:
    cmd = u'scrapy crawl %s -L INFO -a user_name=北娃大王 -a max_page=10' % crawl_name

cmdline.execute(cmd.split())
