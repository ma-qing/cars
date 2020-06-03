# -*- coding: utf-8 -*-
# *-* coding:utf-8 *-*
import os

import requests
from bs4 import BeautifulSoup
import lxml
from lxml import etree
from multiprocessing import Process, Queue
import random
import json
import time
import requests


class Proxies(object):
    """docstring for Proxies"""

    def __init__(self, page=3):
        self.proxies = []
        self.verify_pro = []
        self.page = page
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.get_proxies()
        # self.get_proxies_nn()
    def get_proxies(self):
        page = 1
        page_stop = self.page
        while page < page_stop:
            url = 'http://www.xiladaili.com/http/%s' % page
            html = requests.get(url, headers=self.headers).text
            tree = etree.HTML(html)
            td_url = tree.xpath('//table[@class="fl-table"]/tbody/tr/td[1]/text()')
            for url in td_url:
                url = "http://"+url
                self.proxies.append(url)
            page += 1

    def verify_proxies(self):
        # 没验证的代理
        old_queue = Queue()
        # 验证后的代理
        new_queue = Queue()
        print('verify proxy........')
        works = []
        for _ in range(15):
            works.append(Process(target=self.verify_one_proxy, args=(old_queue, new_queue)))
        for work in works:
            work.start()
        for proxy in self.proxies:
            old_queue.put(proxy)
        for work in works:
            old_queue.put(0)
        for work in works:
            work.join()
        self.proxies = []
        while 1:
            try:
                self.proxies.append(new_queue.get(timeout=1))
            except:
                break
        print('verify_proxies done!')

    def verify_one_proxy(self, old_queue, new_queue):
        while 1:
            proxy = old_queue.get()
            if proxy == 0: break
            protocol = 'https' if 'https' in proxy else 'http'
            proxies = {protocol: proxy}
            try:
                if requests.get('https://www.baidu.com/', proxies=proxies, timeout=2).status_code == 200:
                    print('success %s' % proxy)
                    with open('proxies.txt', 'a') as f:
                        f.write(proxy)
                        f.write("\n")
                    new_queue.put(proxy)
            except:
                print('fail %s' % proxy)


if __name__ == '__main__':
    a = Proxies()
    a.verify_proxies()
    proxie = a.proxies
    proxies_list = []
    for proxy in proxie:
        http_prefix = proxy.split(':')[0]
        proxy_dict = {}
        proxy_dict[http_prefix] = proxy
        proxies_list.append(proxy_dict)

    # with open('proxies.txt', 'w') as f:
        # f.write("")
    # with open('proxies.txt', 'a') as f:
    #     for proxy in proxie:
    #         http_prefix = proxy.split(':')[0]
    #         proxy_dict = {}
    #         proxy_dict[http_prefix] = proxy

            # f.write(json.dumps(proxy_dict) + '\n')
            # f.write(proxy + '\n')