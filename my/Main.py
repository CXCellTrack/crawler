# -*- coding: utf-8 -*-
"""
@author: C.X.
@time: created in 2016/10/4 10:30
@email: xchen-lol@qq.com
"""

import os
import threading as th

from my.login import login_in, HOME_URL, MAIN_URL
from my import utils


#################################################################
# 获取会话，登录主界面
#################################################################
session = login_in()
SAVE_HOME_PATH = r'..\贴图秀'.decode('utf-8')


### 获取主论坛地址
print 'start get_forum_links...'
forums = utils.get_forum_links(session, MAIN_URL)
for name,link in forums.items():
    if name!=u'谈天说地':
        continue
    forum_url = HOME_URL + '/' + link

    ### 获取子论坛地址
    print 'start get_sub_forum_links...'
    sub_forums = utils.get_sub_forum_links(session, forum_url)
    for sub_name, sub_link in sub_forums.items():
        if sub_name!=u'品茶亭':
            continue
        subforum_url = HOME_URL + sub_link

        # 获取帖子地址
        print 'start get_post_link...'
        posts = utils.get_post_links(session, subforum_url)
        for cur_page, title, link in posts:
            if cur_page>1:
                break
            subforum_url = HOME_URL + link

            # 获取图片地址
            img_url = utils.get_img_links(session, subforum_url)
            if len(img_url)==0:
                continue

            # 创建以帖子名的文件夹
            dirname = os.path.join(SAVE_HOME_PATH, title.replace('/', '_'))
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            # 多线程下载
            download_threads = []

            for ii, im_path in enumerate(img_url):
                im_path = im_path if im_path.startswith('/') else '/' + im_path # 图片地址混乱：/upload/..
                postfix = im_path[im_path.rfind('.'):]

                im_full_path = HOME_URL + im_path
                im_name = str(ii) + postfix
                cur_thread = th.Thread(target=utils.download,
                                       args=(session, im_full_path, dirname, im_name))
                download_threads.append(cur_thread)
                cur_thread.start()

            for thread in download_threads:
                thread.join()
            print title, 'done!'








