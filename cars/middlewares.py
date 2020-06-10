# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import os
import random
import time

import redis
from fake_useragent import UserAgent
from scrapy import signals
from scrapy.exceptions import NotConfigured, CloseSpider, IgnoreRequest

from cars.log_utils import SelfLog
from cars.settings import BASE_DIR
from cars.utils import set_redis, sendEmail


class CarsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CarsDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DealDataMiddleware(object):
    add_url_r = set_redis(db=1)
    cookies_deal_r = set_redis(db=2)
    set_url_r = set_redis(4)

    # 获取代理
    def get_proxy(self):
        with open(os.path.join(BASE_DIR, "proxies.txt"), "r") as f:
            date = f.read().splitlines()
            proxy = random.choice(date)
            return proxy

    # # 获取请求头
    # def get_headers(self, request, spider):
    #     # sql = "select ua from useragent order by rand() limit 1;"
    #     cookie_dict = self.get_cookies(request, spider)
    #     cookie = ""
    #     for k, v in cookie_dict.items():
    #         cookie = cookie + k + "=" + v +";"
    #     print("得到的cookie值", cookie)
    #
    #     headers = {
    #         # "User-Agent": dbhelper.readall(sql)[0][0],
    #         "User-Agent": UserAgent().random,
    #         "Content-Type": "text/html; charset=utf-8",
    #         "Host": "www.niuniuqiche.com",
    #         "Cookie": cookie
    #     }
    #
    #     return headers

    def process_request(self, request, spider):
        selflog = SelfLog(spider.name)
        # 根据爬虫名字分别处理爬虫代理和cookie
        if spider.name == "nnqc":
            request.meta['http_proxy'] = self.get_proxy()
            print("{}使用的代理为{},请求url:{}".format(spider.name, request.meta['http_proxy'], request.url))
        elif spider.name == "chezhen":
            request.meta['http_proxy'] = self.get_proxy()
            print("{}使用的代理为{},请求url:{}".format(spider.name, request.meta['http_proxy'], request.url))
        elif spider.name == "car168":
            pass

        # # 添加cookie
        request.cookies = self.get_cookies(request, spider)
        # cookie_dict = self.get_cookies(request, spider)
        # cookie = ""
        # for k, v in cookie_dict.items():
        #     cookie = cookie + k + "=" + v +";"
        # request.headers["User-Agent"] = UserAgent().random
        # request.headers["Content-Type"] = "text/html; charset=utf-8"
        # request.headers["Cookie"] = cookie

        # url = request.url
        # redis_key = request.meta['url_redis']
        # if self.add_url_r.sismember(redis_key, url):
        #     spider.logger.info("该url已经爬取,舍弃:%s"%url)
        #     raise IgnoreRequest
        return None

    def process_response(self, request, response, spider):
        selferrorlog = SelfLog('error')
        selfinfolog = SelfLog(spider.name)
        # 把cookie从能用的库中转移到不能用的库里
        cookie_redis_key_hash = request.meta['cookies_redis']
        cookie_redis_key = request.meta['cookies_redis'] + "_list"
        unuse_cookie_redis_key = request.meta['useless_cookies']
        if response.status == 302:
            print(response.text)
            selferrorlog.logger.error("{spidername}-被封，302重定向到登录界面{cookie}:".format(spidername=spider.name, cookie=request.cookies))
            request = self.dealcookie(request, response, spider)
            return request
        elif "c=com&m=limitPage" in response.text:
            selferrorlog.logger.error("{spidername}-重定向到限制界面, cookie值:{cookie}".format(spidername=spider.name, cookie=request.cookies))
            request = self.dealcookie(request, response, spider)
            return request
        elif "请重新登录" in response.text:
            selferrorlog.logger.error("{spidername}-cookie:{cookies}过期，或者IP不一致，到登录界面".format(spidername=spider.name, cookies=request.cookies))
            request = self.dealcookie(request, response, spider)
            return request
        selfinfolog.logger.info("请求url:{url}使用的cookie:{cookie}".format(url=response.url, cookie=request.cookies))
        return response

    # 处理过期或者被封cookie
    def dealcookie(self, request, response, spider):
        selflog = SelfLog('error')
        cookie_redis_key_hash = request.meta['cookies_redis']
        cookie_redis_key_list = request.meta['cookies_redis'] + "_list"
        unuse_cookie_redis_key = request.meta['useless_cookies']

        redis_member = json.dumps(request.cookies)

        # 查到在hash 中的 手机号
        zset_phone = self.cookies_deal_r.hget(cookie_redis_key_hash, redis_member)
        # 移除在list 和 有用hash 中的 数据 # 在不能用的hash中添加
        self.cookies_deal_r.lrem(cookie_redis_key_list, 0, redis_member)
        self.cookies_deal_r.hdel(cookie_redis_key_hash, redis_member)
        self.cookies_deal_r.hset(unuse_cookie_redis_key, redis_member, zset_phone)
        # 再从redis中取出一个cookie构建request对象
        try:
            popcookie = self.cookies_deal_r.lpop(cookie_redis_key_list)
            self.cookies_deal_r.rpush(cookie_redis_key_list, popcookie)

        except Exception as e:
            selflog.logger.error("{spidername}--cookie 耗尽请补充, 错误信息:{e}".format(spidername=spider.name, e=e))
            # 发送邮件通知，并且最好处理能关闭爬虫
            sendEmail(content="{cookname}cookie耗尽，请尽快处理".format(cookname=cookie_redis_key_list))
            spider.crawler.engine.close_spider(spider, "{cookname}cookie耗尽，关闭爬虫".format(cookname=cookie_redis_key_list))

        else:
            request.cookies = json.loads(popcookie)
            return request

    def get_cookies(self, request, spider):
        selflog = SelfLog('error')
        cookie_redis_key_list = request.meta['cookies_redis'] + "_list"
        cookie_redis_key_hash = request.meta['cookies_redis']
        unuse_cookie_redis_key = request.meta['useless_cookies']
        try:
            # cookies_dict = random.choice(self.cookies_deal_r.zscan(cookie_redis_key)[1])
            # 把cookie 取出来然后放到队尾
            popcookie = self.cookies_deal_r.lpop(cookie_redis_key_list)
            self.cookies_deal_r.rpush(cookie_redis_key_list, popcookie)
        except Exception as e:
            selflog.logger.error("spidername:{spidername} 的cookie 耗尽请补充, 错误信息:{e}".format(spidername=spider.name, e=e))
            # 发送邮件通知，并且最好处理能关闭爬虫
            sendEmail(content="{cookname}cookie耗尽，请尽快处理".format(cookname=cookie_redis_key_list))
            spider.crawler.engine.close_spider(spider, "{cookname}cookie耗尽，关闭爬虫".format(cookname=cookie_redis_key_list))
        else:
            dicts = json.loads(popcookie)
            phonenum = self.cookies_deal_r.hget(cookie_redis_key_hash, popcookie)
            print("{cookie_redis}--手机号：{phonenum}--cookie:{cookie}".format(cookie_redis=cookie_redis_key_hash, phonenum=phonenum, cookie=dicts))
            return dicts




