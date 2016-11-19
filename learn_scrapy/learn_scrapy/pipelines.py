# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import io
import scrapy
import os
import shutil

import time
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import FilesPipeline
# from scrapy.utils.project import get_project_settings # 获取settings.py中的设置


class DmozPipeline(object):
    def process_item(self, item, spider):
        assert spider.name=='dmoz'
        item.update({'spider': spider.name})
        return item


class BuaabtPipeline(object):
    def process_item(self, item, spider):
        assert spider.name=='buaabt'
        ## 获取设置内容
        store_uri = spider.settings['IMAGES_STORE']
        ## 以帖子题目建立目录
        dist_dir = os.path.join(store_uri, item['forum'], item['postname'])
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        for p in item['file_paths']:
            src = os.path.join(store_uri, 'full', p)
            ## 目标处无文件，则移动过去
            objfile = os.path.join(dist_dir, p)
            if os.path.exists(objfile):
                os.remove(objfile)
            else:
                shutil.move(src, dist_dir)
        return item


class WeiboPipeline(object):
    user_names = dict()

    def process_item(self, item, spider):
        assert spider.name=='weibo'
        ## 获取设置内容
        store_uri = spider.settings['FILES_STORE']
        ## 统计最后得到的图片数目
        img_num = len(filter(lambda x:x[1]!=item['user_info']['headimg'],
                             item['image_datas']))
        ## 以user_name、post_id建立目录
        user_name = item['name']
        post_id = item['weibo_info']['post_id']
        user_dir = os.path.join(store_uri, user_name)
        post_dir = os.path.join(user_dir, 'post_%s'% post_id + ('[%sP]'% img_num)*bool(img_num))
        for dir_ in [user_dir, post_dir]:
            if not os.path.exists(dir_):
                os.makedirs(dir_)

        ## 如果是第一次访问该姓名，则建立个人档案
        if user_name not in self.user_names.keys():
            self.user_names.update({user_name: set()})
            objfile = os.path.join(user_dir, u'个人资料.txt')
            user_info = dict(item['user_info'])
            user_info.update({u'name': user_name})
            with io.open(objfile, 'w', encoding='utf-8') as f:
                for k, v in user_info.iteritems():
                    f.write('[%s] : %s\n' % (k, v)) # k,v必须都是unicode

        ## 如果是第一次访问该帖子，则记录帖子内容
        if post_id not in self.user_names[user_name]:
            self.user_names[user_name].add(post_id)
            objfile = os.path.join(post_dir, u'帖子内容.txt')
            with io.open(objfile, 'w', encoding='utf-8') as f:
                f.write('%s' % item["weibo_info"]["content"])

        ## 将下载好的图片移动进去
        for path, url in item['image_datas']:
            src = os.path.join(store_uri, 'full', path)
            ## 帖子图片->post_dir，头像->user_dir
            if url==item['user_info']['headimg']:
                objfile = os.path.join(user_dir, 'headimg.jpg')
            else:
                objfile = os.path.join(post_dir, path)
            ## 目标文件不存在，则移动过去
            if not os.path.exists(objfile):
                shutil.move(src, objfile)
        return item


# =========================================================== #
# 使用了ImagesPipeline来进行图片下载（重写item_completed方法）
# =========================================================== #
class MyImagesPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        ## 设置访问延迟 （可解决每次访问能够成功，但是下载总是失败的问题）
        time.sleep(0.5)
        return [scrapy.Request(x) for x in item.get(self.files_urls_field, [])]

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.files_urls_field in item.fields:
            ## 判断是否图片为空
            image_datas = [(x['path'].split('/')[-1], x['url']) for ok, x in results if ok]
            if not image_datas:
                raise DropItem("Item contains no files")
            # 下载成功的名称和url路径
            item['image_datas'] = image_datas
        return item
