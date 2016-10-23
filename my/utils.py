# -*- coding: utf-8 -*-
"""
@author: C.X.
@time: created in 2016/10/23 14:01

"""
import os
import re

from bs4 import BeautifulSoup as BS
from my.login import HOME_URL


##############################################
# 将网页内容保存到文件
##############################################
def save_to_file(response):
    if response.status_code!=200:
        Warning('status_code=%d' % response.status_code)
        return
    fid = open('saveres.xml', 'w')
    fid.write(response.content)
    fid.close()
    print 'saveres.xml saved successfully!'


##############################################
# 下载资源
##############################################
def download(session, url, dirname, picname):
    savepath = os.path.join(dirname, picname)
    rr = session.get(url, timeout=10, stream=True)
    with open(savepath, 'wb') as sav:
        sav.writelines(rr.iter_content(chunk_size=1024 * 10))
    print picname, 'successfully downloaded!'


##############################################
# 解析大类论坛地址
##############################################
def get_forum_links(session, main_url):
    r_main = session.get(url=main_url, timeout=3)
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
def get_sub_forum_links(session, forum_url):
    rps = session.get(url=forum_url, timeout=3)
    soup = BS(rps.text, "html.parser")
    cl_list = soup.find(name='div', class_='main cl list', id='subforum')
    cl_list = cl_list.findChild(class_='fi', recursive=False)
    ## 记录子论坛
    sub_forums = dict()
    for sub in cl_list.find_all(name='th', class_=re.compile('notopic')):
        sub_forums.update({sub.h2.a.img['alt']:sub.h2.a['href']})
    return sub_forums


##############################################
# 解析每个帖子地址
##############################################
def get_post_links(session, subforum_url, page=1):
    if subforum_url is None:
        return
    ## 连接网页
    print 'pocess page %d\n' % page
    rps = session.get(url=subforum_url, timeout=3)
    soup = BS(rps.text, "html.parser")
    table = soup.find(name='table', attrs={'id':'threadlist'})
    tbodys = table.findChildren(name='tbody', recurse=False)
    ## 找到分割线 {u'class': [u'separation']}
    bool_tbs = map(lambda x:'class' in x.attrs.keys(), tbodys)
    ## 有分割线，说明是首页;如果没有分割线，说明是后面的页
    i_st = bool_tbs.index(True) + 1 if any(bool_tbs) else 0
    tbodys = tbodys[i_st:]
    ## 寻找下一页链接
    next_btn = soup.find(name='div', class_="big_nextbtn")
    if next_btn is None:
        next_page = None
    else:
        next_page = HOME_URL + next_btn.a['href']
        page += 1
    ## 解析帖子标题
    for tb in tbodys:
        tmp = tb.tr.th.a
        yield (page - 1, tmp.text, tmp['href'])
    get_post_links(session, next_page, page)


##############################################
# 解析出帖子中的图片地址
##############################################
def get_img_links(session, post_url):
    r_im = session.get(post_url, timeout=3)
    ## 自动解析经常不全，还是用正则比较好
    # 注意贪婪/吝啬模式的使用
    first_table = re.findall(re.compile('<td class="postcontent">.*?(?=<td class="plc">)',
                                        re.DOTALL), r_im.text)
    if len(first_table)==0:
        return []
    soup = BS(first_table[0], "html.parser")
    imgs = soup.find_all(name='img', imageid=re.compile('\d+'), src=re.compile('upload/.+'))
    return [im['src'] for im in imgs]
