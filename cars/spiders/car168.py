# -*- coding: utf-8 -*-
import datetime
import json
import random
import re
import time

import scrapy
from fake_useragent import UserAgent
from scrapy import Request

from cars.CONSTANT import China, ChinaImport, USA, Canada, Mexico, European
from cars.items import CarStyleItem
from cars.log_utils import SelfLog
from cars.utils import Mysqlpython, set_redis, deal_year, deal_style, deal_displacement, deal_updatetime, \
    deal_guideprice

cookie_r = set_redis(2)
type_r = set_redis()
dbhelper = Mysqlpython()
set_url_r = set_redis(4)

cookies_car168 = "cookies_car168"
unuseless_cookies_car168 = "unuseless_cookies_car168"
url_redis = "car168"
url_redis_car168 = "car168_urls"

class Car168Spider(scrapy.Spider):
    name = 'car168'
    allowed_domains = ['www.chehang168.com']
    start_urls = ['http://www.chehang168.com/', 'http://www.chehang168.com/index.php?c=index&m=allBrands', "http://www.chehang168.com/index.php?c=index&m=Cardata"]
    selflog = SelfLog(name)
    
    def get_headers(self):
        headers = {
            "User-Agent": UserAgent().random,
        }
        return headers

    i = 0

    def start_requests(self):
        url = "http://www.chehang168.com/index.php?c=index&m=series&psid=%s"

        for key in type_r.keys():
            key = key.decode()
            request = Request(url=url%key, callback=self.parse_select_cartype, headers=self.get_headers())#, cookies=self.get_cookies(""))
            value = type_r.get(key)
            if value:
                request.meta['type'] = value.decode()
            else:
                request.meta['type'] = None

            # 存放url
            request.meta['url_redis'] = url_redis
            # 存放cookie
            request.meta['cookies_redis'] = cookies_car168
            # 存放不能用的cookie
            request.meta['useless_cookies'] = unuseless_cookies_car168
            yield request

    # 列表详情页信息
    def parse_select_cartype(self, response):
        lastcookie = response.request.cookies
        # 这里分情况，当是第一页时构建从第二页到最后一页的请求， 如果不是第一页则跳过
        isfirstpage = response.xpath('//p[@class="pagenum"]/span[@class="current"]/text()').extract_first()
        if isfirstpage == "1":
            lastpage = response.xpath('//p[@class="pagenum"]//a[last()-2]/text()').extract_first()
            pageurl = response.url + "&pricetype=0&page=%s"
            for pagenum in range(2, int(lastpage)+1):
                nextpage_url = pageurl%pagenum
                # self.selflog.logger.info("继续请求下一页信息:%s" % nextpage_url)
                request_nextpage = response.follow(url=nextpage_url, callback=self.parse_select_cartype,
                                                   headers=self.get_headers())#, cookies=self.get_cookies(lastcookie))
                request_nextpage.meta['type'] = response.meta['type']
                # 存放url
                request_nextpage.meta['url_redis'] = url_redis
                # 存放cookie
                request_nextpage.meta['cookies_redis'] = cookies_car168
                # 存放不能用的cookie
                request_nextpage.meta['useless_cookies'] = unuseless_cookies_car168
                yield request_nextpage

        # type_label = response.meta['type_lable']
        # 车型
        #***新方法的brand, type_lable, type
        self.i += 1
        type_lable = response.xpath('//div[@class="sx_left o_cf"]/a[1]/span/text()').extract_first()
        brand = response.xpath('//div[@class="ch_crumb o_w mar8"]/a[3]/text()').extract_first()
        base_car_style = response.xpath('//div[@class="cheyuan_list"]/ul[2]/li')

        for li in base_car_style:
            car_style = li.xpath('./div/h3/a/text()').extract_first()
            # 类型去空格处理后使用一个空格隔开
            car_style = deal_style(car_style)
            # 配置没有为空
            config = li.xpath('./p[@class="c2"]/text()').extract_first()
            # 排量
            displacement = deal_displacement(car_style, self)
            # 年款
            year = deal_year(car_style, self)

            # 进口方式
            version = li.xpath('./p[@class="c1"]/text()').extract_first()
            version = str(version)
            if China in version or "国产" in version:
                version_num = 0
            elif ChinaImport in version:
                version_num = 1
            elif USA in version:
                version_num = 2
            elif Canada in version:
                version_num = 3
            elif Mexico in version:
                version_num = 4
            elif European in version:
                version_num = 5
            else:
                self.selflog.logger.info("车型{car_style}的进口版本不在规定内".format(car_style=car_style))
                version_num = None

            # 指导价: 指导价:25.27万下20点
            guide_price = li.xpath('./div/h3/b/text()').extract_first()
            guide_price = deal_guideprice(guide_price, car_style, self)
            # 价钱标识 ￥
            price_flag = li.xpath('./div/span/text()').extract_first()
            price = li.xpath('./div/span/b/text()').extract_first()
            # 成交量： 车源成交量：3单
            volume = li.xpath('./p/cite[4]/text()').extract_first()
            if volume:
                search_volume = re.search("(\d+)单", volume)
                if search_volume:
                    volume = search_volume.group(1)

            # 更新时间
            updatetime = li.xpath('./p[@class="c3"]/cite[1]/text()').extract_first()
            updatetime = deal_updatetime(updatetime)
            # 详情页信息
            detail_url = li.xpath('./div/h3/a/@href').extract_first()
            if detail_url:
                detail_url = self.start_urls[0] + str(detail_url)
            else:
                detail_url = ""

            carstyleitem = CarStyleItem()
            carstyleitem['brand'] = brand
            carstyleitem["type"] = response.meta['type']
            carstyleitem['year'] = year
            carstyleitem['style'] = car_style
            carstyleitem['configuration'] = config
            carstyleitem['displacement'] = displacement
            carstyleitem['volume'] = volume
            carstyleitem['status'] = None
            carstyleitem['version'] = version_num
            carstyleitem['guide_price'] = guide_price
            carstyleitem['price'] = price
            carstyleitem['platform'] = 1
            carstyleitem['rediskey'] = url_redis
            # 详情页的url 和更新时间
            carstyleitem['detail_url'] = detail_url
            carstyleitem['updatetime'] = updatetime

            yield carstyleitem

        # 把这一页的url信息set进redis中
        # 如果已经爬取过的话并不会触发添加条件,会被过滤掉，
        # 如何判断已经全部添加。。。。。
        set_url_r.sadd(url_redis_car168, response.url)


