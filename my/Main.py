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
from my.utils import valid_filename

session = login_in()
# 选择爬哪个子论坛
SUBFORUM_NAMES = [u'贴图秀', u'缘来是你']
subforum_name = SUBFORUM_NAMES[1]
save_homepath = os.path.join('..', subforum_name)
if not os.path.exists(save_homepath):
    os.mkdir(save_homepath)


MAX_PAGES = 5
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
        if sub_name!=subforum_name:
            continue
        print 'start crawl subforum', subforum_name
        subforum_url = HOME_URL + sub_link

        # 获取帖子地址
        print 'start get_post_link...'
        posts = utils.get_post_links(session, subforum_url, MAX_PAGES) # 只抓 MAX_POSTS 页内帖子
        for title, post_link in posts:
            post_url = HOME_URL + post_link
            # 获取图片地址
            img_url = utils.get_img_links(session, post_url)
            if len(img_url)==0:
                print 'image not found in', title
                continue

            # 创建以帖子名的文件夹
            dirname = os.path.join(save_homepath, valid_filename(title))
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






