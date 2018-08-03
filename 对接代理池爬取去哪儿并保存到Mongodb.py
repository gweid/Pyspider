#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-07-20 17:26:02
# Project: Qunarr

import pymongo
import requests
from pyspider.libs.base_handler import *

# 连接Mongodb
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.Qunar
collection = db.GongLve


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://travel.qunar.com/travelbook/list.htm', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        # 对接代理池的API
        proxy = requests.get('http://localhost:5200/random').text
        for each in response.doc('li > .tit > a').items():
            self.crawl(each.attr.href, callback=self.detail_page, proxy=proxy)
        next = response.doc('.next').attr.href
        self.crawl(next, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        data = {
            "标题": response.doc('title').text(),
            "出发日期": response.doc('.when .data').text(),
            "旅游天数": response.doc('.howlong .data').text() + '天',
            "出行人物": response.doc('.who .data').text(),
            "玩法": response.doc('.how .data .data').text(),
            "旅行日记": response.doc('.b_panel_schedule .text').text().replace('\xa0', '').replace('\n', ' ')
        }
        collection.insert(data)
