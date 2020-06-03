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
from cars.cookies import cookies168_list, cookies168_list2
from cars.items import CarStyleItem
from cars.log_utils import SelfLog
from cars.utils import Mysqlpython, set_redis

cookie_r = set_redis(2)
type_r = set_redis()
dbhelper = Mysqlpython()

cookies_car168 = "cookies_car168"
unuseless_cookies_car168 = "unuseless_cookies_car168"
url_redis = "car168"

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

    def parse_select_cartype(self, response):
        lastcookie = response.request.cookies
        # 这里分情况，当是第一页时构建从第二页到最后一页的请求， 如果不是第一页则跳过
        isfirstpage = response.xpath('//p[@class="pagenum"]/span[@class="current"]/text()').extract_first()
        if isfirstpage == "1":
            lastpage = response.xpath('//p[@class="pagenum"]//a[last()-2]/text()').extract_first()
            # nextpage_base = response.xpath('//p[@class="pagenum"]//a[last()]')
            # # 如果a 连接中有下一页信息则请求下一页
            # if nextpage_base.xpath('./text()').extract_first() == "下一页":
            #     nextpage_url = nextpage_base.xpath('./@href').extract_first()
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
        time.sleep(random.randint(1, 5))
        self.i += 1
        type_lable = response.xpath('//div[@class="sx_left o_cf"]/a[1]/span/text()').extract_first()
        brand = response.xpath('//div[@class="ch_crumb o_w mar8"]/a[3]/text()').extract_first()
        base_car_style = response.xpath('//div[@class="cheyuan_list"]/ul[2]/li')

        for li in base_car_style:
            carstyleitem = CarStyleItem()
            # carstyleitem['brand'] = response.meta['brand']
            # carstyleitem["type"] = response.meta['type']
            carstyleitem['brand'] = brand
            carstyleitem["type"] = response.meta['type']

            car_style = li.xpath('./div/h3/a/text()').extract_first()
            # 类型去空格处理后使用一个空格隔开
            if car_style:
                car_style = " ".join(car_style.split())
            carstyleitem['style'] = car_style
            # 详情页信息
            detail_url = li.xpath('./div/h3/a/@href').extract_first()
            if detail_url:
                detail_url = self.start_urls[0]+ str(detail_url)
            else:
                detail_url = ""

            # 配置没有为空
            config = li.xpath('./p[@class="c2"]/text()').extract_first()
            # 配置
            carstyleitem['configuration'] = config

            # 排量
            car_style = str(car_style)
            search_displacement = re.search("\d+\.\d+Li|\d+Li|\d+\.\d+Le|\d+Le|\d+\.\d+T|\d+T|\d+\.\d+L|\d+L", car_style)
            if search_displacement:
                displacement = search_displacement.group()
            else:
                self.selflog.logger.info("车型:{car_style}未匹配到排量信息".format(car_style=car_style))
                displacement = None

            carstyleitem['displacement'] = displacement

            # 年款
            search_year = re.search('\d+款', car_style)
            if search_year:
                year = search_year.group()
            else:
                year = None
                self.selflog.logger.info("车型{car_style}未匹配到年款信息".format(car_style=car_style))

            carstyleitem['year'] = year

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
            carstyleitem['version'] = version_num

            # 指导价: 指导价:25.27万下20点
            guide_price = li.xpath('./div/h3/b/text()').extract_first()
            if guide_price:
                # 匹配后的价格 XX.XX万
                select_guide_price = re.search("\d+\.\d+万|\d+万", guide_price, re.I)
                if select_guide_price:
                    guide_price = select_guide_price.group()
            carstyleitem['guide_price'] = guide_price
            # 价钱标识 ￥
            price_flag = li.xpath('./div/span/text()').extract_first()
            price = li.xpath('./div/span/b/text()').extract_first()
            carstyleitem['price'] = price
            # 成交量： 车源成交量：3单
            volume = li.xpath('./p/cite[4]/text()').extract_first()
            if volume:
                search_volume = re.search("(\d+)单", volume)
                if search_volume:
                    volume = search_volume.group(1)

            # 更新时间
            updatetime = li.xpath('./p[@class="c3"]/cite[1]/text()').extract_first()
            # datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            if updatetime:
                if "-" in updatetime:
                    updatetime = str(datetime.datetime.now().year) + "-"+ updatetime +" 00:00"
                elif ":" in updatetime:
                    updatetime = datetime.datetime.now().strftime('%Y-%m-%d') + " " + updatetime
            else:
                updatetime = ""

            carstyleitem['volume'] = volume
            carstyleitem['status'] = None
            carstyleitem['platform'] = 1
            carstyleitem['rediskey'] = url_redis
            # 详情页的url 和更新时间
            carstyleitem['detail_url'] = detail_url
            carstyleitem['updatetime'] = updatetime

            yield carstyleitem
