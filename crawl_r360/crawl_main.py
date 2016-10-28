# -*- coding: utf-8 -*-
"""
@author: chenxu
@contact: chenxu@rong360.com
@project: Risk Control
@file: crawl_main
@time: 2016/10/27 18:03
"""

import requests
from bs4 import BeautifulSoup as BS
import re
import os
import threading as th



HOME_URL = 'http://home.rong360.com/'
START_URL = HOME_URL + 'forum.php'


# =========================================================== #
# 获得几个子论坛的地址
# =========================================================== #
def get_subforum():
    rsp = requests.get(START_URL, timeout=2)
    soup = BS(rsp.text, 'lxml')
    rsp.close()
    bmw = soup.find(name='div', class_='bm bmw cl')
    table = bmw.find(name='table')
    res = table.find_all(name='td', class_='fl_icn')
    for x in res:
        yield x.a['href'], x.a.img['alt']


# =========================================================== #
# 获得每个帖子的地址，可指定最大页数
# =========================================================== #
def get_posts(full_sub_link, page=1, max_page=1):
    if page > max_page > 0:
        return []
    print 'process page %d ...' % page
    rsp = requests.get(full_sub_link, timeout=2)
    soup = BS(rsp.text, 'lxml')
    rsp.close()
    # 若max_page=0则不限最大页数，此时需要找到最大页数
    if page==1 and max_page==0:
        pagedata = soup.find(name='span', title=re.compile(u'共\s*\d+\s*页'))
        if pagedata is None:
            max_page = 1
        else:
            max_page = int(re.compile(u'共\s*(\d+)\s*页').search(pagedata['title']).group(1))

    posts = soup.find_all(name='th', class_='new')
    final_res = []
    for pst in posts:
        data = pst.find(name='a', class_='s xst')
        final_res.append((data.text, data['href']))
    ## 寻找下一页地址
    next_page_link = full_sub_link + '&page=' + str(page + 1)
    final_res.extend(get_posts(next_page_link, page + 1, max_page))
    return final_res


# =========================================================== #
# 获取图片地址
# =========================================================== #
def get_image(full_post_link):
    rsp = requests.get(full_post_link, timeout=2)
    soup = BS(rsp.text, 'lxml')
    rsp.close()
    td = soup.find(name='td', class_='t_f')
    try:
        img = td.find(name='ignore_js_op').img
        return img['file']
    except:
        return None


# =========================================================== #
# 下载图片
# =========================================================== #
def download(url, dirname, picname):
    savename = os.path.join(dirname, picname) + '.jpg'
    if os.path.exists(savename):
        print picname, 'exists'
        return
    rps = requests.get(url, timeout=5, stream=True)
    # 尝试下载次数
    download_tries = 1
    ## 针对下载有可能失败的问题
    while True:
        try:
            with open(savename, 'wb') as sav:
                sav.writelines(rps.iter_content(chunk_size=1024))
            rps.close()
            break
        except:
            print 'retry download for', download_tries, 'times...'
            download_tries += 1
    print picname, 'download successfully!'


# =========================================================== #
# 进行下载
# =========================================================== #
SUB_NAME = u'员工风采'
for sub_link, sub_name in get_subforum():
    if sub_name!=SUB_NAME:
        continue
    if not os.path.exists(SUB_NAME):
        os.mkdir(SUB_NAME)
    print 'start crawl from', sub_name, '...'
    full_sub_link = HOME_URL + sub_link
    ## 寻找帖子地址

    download_threads = []
    for name, post_link in get_posts(full_sub_link, max_page=0):
        # print name, post_link
        full_post_link = HOME_URL + post_link

        ## 找到图片地址
        img_link = get_image(full_post_link)
        if img_link is None:
            continue
        full_img_link = HOME_URL + img_link

        ## 多线程下载
        cur_thread = th.Thread(target=download, args=(full_img_link, sub_name, name))
        download_threads.append(cur_thread)
        cur_thread.start()

    for thread in download_threads:
        thread.join()
    print sub_name, 'done!'
