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
    cmd = 'scrapy crawl %s -L INFO' % crawl_name

cmdline.execute(cmd.split())
