# -*- coding: utf-8 -*-
"""
@author: C.X.
@time: created in 2016/10/4 10:30
@email: xchen-lol@qq.com
"""

from bs4 import BeautifulSoup as BS
import requests
import re
import os
import threading as th


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


##############################################
# 模拟登录
##############################################
home_url = 'http://buaabt.cn'
login_url = home_url + '/login.aspx'
Main_url = home_url + '/forumindex.aspx'
save_home_path = r'C:\Users\xchen\Desktop\贴图秀'.decode('utf-8')


def login_in():
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
    return session, r_main

# 获取会话
print 'start login_in...'
session, r_main = login_in()


##############################################
# 使用BS4解析网页内容
##############################################
def get_forum_links():
    soup = BS(r_main.content, "html.parser")
    # 找出所有的子论坛
    titlebar = soup.find_all(name='div', class_='titlebar xg2')
    forums = dict()
    for tb in titlebar:
        forums[tb.h2.text.strip()] = tb.h2.a['href']
    return forums


##############################################
# 解析子论坛地址
##############################################
def get_sub_forum_links(tmp_url):
    r_s = session.get(url=tmp_url, timeout=3000)
    # save_to_file(r_s)
    f_soup = BS(r_s.text, "html.parser")
    cl_list = f_soup.find(name='div', class_='main cl list', id='subforum')
    cl_list = cl_list.findChild(class_='fi', recursive=False)
    ## 记录子论坛
    sub_forums = dict()
    for sub in cl_list.find_all(name='th', class_=re.compile('notopic')):
        sub_forums[sub.h2.a.img['alt']] = sub.h2.a['href']
    return sub_forums


##############################################
# 解析每个帖子地址
##############################################
def get_post_links(tmp_url, page=1):
    if tmp_url is None:
        return
    ## 连接网页
    print 'pocess page %d\n' % page
    r_s = session.get(url=tmp_url, timeout=3000)
    f_soup = BS(r_s.text, "html.parser")
    table = f_soup.find(name='table', attrs={'id': 'threadlist'})
    tbodys = table.findChildren(name='tbody', recurse=False)
    ## 找到分割线 {u'class': [u'separation']}
    bool_tbs = map(lambda x:'class' in x.attrs.keys(), tbodys)
    if any(bool_tbs):
        ## 有分割线，说明是首页
        i_s = bool_tbs.index(True) + 1
    else:
        ## 如果没有分割线，说明是后面的页
        i_s = 0
    tbodys = tbodys[i_s:]
    ## 寻找下一页链接
    next_btn = f_soup.find(name='div', class_="big_nextbtn")
    if next_btn is None:
        next_page = None
    else:
        next_page = home_url + next_btn.a['href']
        page += 1
    ## 解析帖子标题
    for tb in tbodys:
        tmp = tb.tr.th.a
        yield (page-1, tmp.text, tmp['href'])
    get_post_links(next_page, page)


##############################################
# 解析出帖子中的图片地址
##############################################
def get_img_path(tmp_url):
    r_im = session.get(tmp_url, timeout=3000)
    ## 自动解析经常不全，还是用正则比较好
    if 0:
        first_post = re.findall(re.compile('<div id="firstpost">.*(?=<div class="newrate cl")',
                                        re.DOTALL), r_im.text)
        soup = BS(first_post[0], "html.parser")
    else:
        # 注意贪婪/吝啬模式的使用
        first_table = re.findall(re.compile('<td class="postcontent">.*?(?=<tr>)',
                                 re.DOTALL), r_im.text)
        soup = BS(first_table[0], "html.parser")

    imgs = soup.find_all(name='img', imageid=re.compile('\d+'), src=re.compile('/*upload/.+'))
    return [im['src'] for im in imgs]


##############################################
# 下载资源
##############################################
def download(url, dirname, picname):
    savepath = os.path.join(dirname, picname)
    rr = session.get(url, timeout=2, stream=True)
    with open(savepath, 'wb') as sav:
        sav.writelines(rr.iter_content(chunk_size=1024*10))
    print picname, 'successfully downloaded!'



print 'start get_forum_links...'
forums = get_forum_links()
for lk in forums.values():
    if lk!=u'showforum-1.aspx':
        continue
    tmp_url = home_url + '/' + lk
    print 'start get_sub_forum_links...'
    sub_forums = get_sub_forum_links(tmp_url)
    for sub_lk in sub_forums.values():
        if sub_lk!=u'/showforum-2.aspx':
            continue
        tmp_url = home_url + sub_lk
        # 获取帖子地址
        print 'start get_post_link...'
        posts = get_post_links(tmp_url)
        for cur_page, title, link in posts:
            if cur_page>1:
                break
            # 创建以帖子名的文件夹
            dirname = os.path.join(save_home_path, title.replace('/', '_'))
            if not os.path.exists(dirname):
                os.mkdir(dirname)

            tmp_url = home_url + link
            # 获取图片地址
            download_threads = []
            img_path = get_img_path(tmp_url)
            for ii,im in enumerate(img_path):
                im = im if im.startswith('/') else '/'+im # 图片地址混乱：/upload/..
                im_path = home_url + im
                im_name = str(ii) + '.jpg'
                cur_thread = th.Thread(target=download, args=(im_path, dirname, im_name))
                download_threads.append(cur_thread)
                cur_thread.start()

            for thread in download_threads:
                thread.join()
            print title, 'done!'








