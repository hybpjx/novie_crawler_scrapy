# -*- coding: utf-8 -*-
# @Time    : 2022/6/30 11:21
# @Author  : lzc
# @Email   : hybpjx@163.com
# @File    : QiDianNovelPro.py
# @Software: PyCharm
import random
import re
import time
from urllib.parse import urljoin
from fontTools.ttLib import TTFont
import fake_useragent
import requests
from lxml import etree


class QiDianNovel:
    def __init__(self):
        self.base_url = "https://www.qidian.com/all/"
        self.session = requests.Session()
        self.item = {}
        self.header = {
            "User-Agent": fake_useragent.UserAgent().random
        }

    def fetch(self, url):
        response = self.session.get(url, headers=self.header)
        return response



    def parse_font(self, html):
        # 获得加密后的数字
        encrypted_number = re.findall('</style><span class=".*?">(.*?)</span>', html)
        # print(encrypted_number)
        # 利用正则获取动态url
        font_url = re.findall(r"format\('eot'\); src: url\('(.*?)'\) format\('woff'\)", html)[0]
        # 发送请求，下载字体加密文件
        font_response = self.fetch(font_url)
        with open('font/jiemi.woff', 'wb')as f:
            f.write(font_response.content)
        # 解析字体解密文件 并且 创建TTFont对象
        font_obj = TTFont('font/jiemi.woff')
        # 转换成xml明文格式
        font_obj.saveXML('font/jiemi.xml')
        mapping_dict = self.font_encode(encrypted_number, font_obj)
        # 通过匹配response去掉特殊符号的值 和 改成阿拉伯数字后的关系映射表，把密文改成明文  100196   =》 3
        for i in encrypted_number:  # 去掉response去掉特殊符号的值[[],[],[]]
            # print(i)  #  ['100388', '100389', '100388', '100385', '100385']
            for index, num in enumerate(i):  # 100388
                # print(index,num)
                for k in mapping_dict:  # 改成阿拉伯数字后的关系映射表
                    # print(k)
                    if num == str(k):
                        i[index] = mapping_dict[k]
        # print("解析之后的月票数", encrypted_number)
        # 对单个明文进行拼接成完整的月票数
        list_ = []
        for i in encrypted_number:
            j = ''
            for k in i:
                j += k
            list_.append(j)
        return list_

    def font_encode(self, encrypted_number, font_obj):
        # 获取映射表
        mapping_dict = font_obj.getBestCmap()
        # print("字体加密映射表", mapping_dict)
        for index, i in enumerate(encrypted_number):
            new_font_list = re.findall(r'\d+', i)  # 去掉特殊符号 &#  &# ;
            encrypted_number[index] = new_font_list
        dict_e_a = {
            "one": '1', "two": '2',
            "three": '3', "four": '4',
            "five": "5", "six": '6',
            "seven": "7", "eight": '8',
            "nine": '9',
            "zero": '0', 'period': "."
        }
        for i in mapping_dict:
            # 遍历dict_e_a
            # print(i)
            for j in dict_e_a:
                # dict_的值等于dict_e_a的键
                if mapping_dict[i] == j:
                    mapping_dict[i] = dict_e_a[j]
        # print("替换成数字后的关系映射表", mapping_dict)
        return mapping_dict

    def get_data(self):
        # 解析 url
        html = self.fetch(self.base_url).text
        # tree对象 不解释
        tree = etree.HTML(html)
        # 拿到 字体列表
        font_list=self.parse_font(html)

        for index,(font,li) in enumerate(zip(font_list,tree.xpath('//*[@id="book-img-text"]/ul/li'))):
            print(f"第{index+1}本小说爬取....")
            # 小说 链接
            self.item["novel_url"] = urljoin(self.base_url, li.xpath(".//h2/a/@href")[0])

            # 小说名字
            self.item["novel_name"] = li.xpath('.//h2/a/text()')[0]

            # 小说作者名
            self.item["novel_author_name"] = li.xpath('.//p[starts-with(@class,"author")]/a/text()')[0]
            # 小说作者链接
            self.item["novel_author_url"] = urljoin(self.base_url, li.xpath('.//p[starts-with(@class,"author")]/a/@href')[0])
            # 小说简介
            self.item['novel_description'] = li.xpath('.//p[starts-with(@class,"intro")]/text()')[0]
            # 小说 字数
            self.item['novel_number'] = font+"万字"
            # 防止反爬，随即休眠1到2秒
            time.sleep(random.randint(1, 2))
            print(self.item)


if __name__ == '__main__':
    QiDianNovel().get_data()
