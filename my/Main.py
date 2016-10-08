# -*- coding: utf-8 -*-
"""
@author: C.X.
@time: created in 2016/10/4 10:30
@email: xchen-lol@qq.com
"""

from bs4 import BeautifulSoup as BS
import requests
import re


##############################################
# 将网页内容保存到文件
##############################################
def save_to_file(res):
    if res.status_code!=200:
        Warning('status_code=%d' % res.status_code)
        return
    fid = open('saveres.xml', 'w')
    fid.write(res.content)
    fid.close()
    print 'saveres.xml saved successfully!'
    return


##############################################
# 模拟登录
##############################################
login_url = 'http://buaabt.cn/login.aspx'
Main_url = 'http://buaabt.cn/forumindex.aspx'

## 先使用post登录获取cookies
data = {'username': '965001147',
        'password': 'chenxu'}
r_login = requests.post(url=login_url, data=data, timeout=3000)
# save_to_file(r_login)

## 登录进入主页面
if 0:
    r_main = requests.get(url=Main_url, cookies=r_login.cookies, timeout=3000)
else:
    # 使用session不必每次都加上cookies
    session = requests.Session()
    session.cookies = r_login.cookies
    r_main = session.get(url=Main_url, timeout=3000)
# save_to_file(r_main)


##############################################
# 使用BS4解析网页内容
##############################################
soup = BS(r_main.content, "html.parser")
# 找出所有的子论坛
forum_links = soup.find_all(name='a', href=re.compile('/showforum-.*.aspx'))
