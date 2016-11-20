# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:12:31 2016

@author: Administrator
"""

from scrapy import cmdline 


crawl_name = 'douban'
DEBUG = 0
if DEBUG:
    cmd = 'scrapy crawl %s -L DEBUG -o debug.json' % crawl_name
else:
    if crawl_name=='weibo':
        cmd = u'scrapy crawl %s -L INFO -a user_name=0木头-木头0 -a max_page=1' % crawl_name
    elif crawl_name=='douban':
        cmd = 'scrapy crawl %s -L INFO' % crawl_name


cmdline.execute(cmd.split())
