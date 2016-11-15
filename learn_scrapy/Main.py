# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:12:31 2016

@author: Administrator
"""

from scrapy import cmdline 

cmd = 'scrapy crawl dmoz -L INFO -o res.json'
cmdline.execute(cmd.split())
