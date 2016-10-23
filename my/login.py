# -*- coding: utf-8 -*-
"""
@author: C.X.
@time: created in 2016/10/23 14:08

"""
import requests


##############################################
# 模拟登录
##############################################
HOME_URL = 'http://buaabt.cn'
LOGIN_URL = HOME_URL + '/login.aspx'
MAIN_URL = HOME_URL + '/forumindex.aspx'


def login_in():
    print 'start login_in...'
    ## 先使用post登录获取cookies
    data = {'username': '965001147',
            'password': 'chenxu'}
    r_login = requests.post(url=LOGIN_URL, data=data, timeout=3)

    ## 登录进入主页面
    if 0:
        r_main = requests.get(url=MAIN_URL, cookies=r_login.cookies, timeout=3)
    else:
        # 使用session不必每次都加上cookies
        session = requests.Session()
        session.headers = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/50.0.2661.102 Safari/537.36'
        session.cookies = r_login.cookies
    return session





