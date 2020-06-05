# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import random
import re

import scrapy
from fake_useragent import UserAgent
from scrapy import Request

# 账号：17061084088
# 密码：ma123456
from cars.CONSTANT import USA, Canada, Mexico, European, China, ChinaImport
from cars.items import CarStyleItem, CarDetailItem
from cars.log_utils import SelfLog
from cars.settings import BASE_DIR
from cars.utils import Mysqlpython, set_redis, deal_style, deal_year, deal_displacement, deal_guideprice

r_zet_cookie = set_redis(2)
set_url_r = set_redis(4)
dbhelper = Mysqlpython()
cookies_nnqc = "cookies_nnqc"
unuseless_cookies_nnqc = "unuseless_cookies_nnqc"
url_redis = "nnqc"
url_redis_nnqc = "nnqc_urls"


class NnqcSpider(scrapy.Spider):
    name = 'nnqc'
    allowed_domains = ['www.niuniuqiche.com']
    start_urls = ['http://www.niuniuqiche.com/', 'http://www.niuniuqiche.com/v2/brands']
    i = 0
    selflog = SelfLog(name)
    def get_headers(self):
        # sql = "select ua from useragent order by rand() limit 1;"
        headers = {
            # "User-Agent": dbhelper.readall(sql)[0][0],
            "User-Agent": UserAgent().random,
            "Content-Type": "text/html; charset=utf-8",
            "Host": "www.niuniuqiche.com",
        }

        return headers


    def get_cookie(self, newcookie):

        cookies_dict = random.choice(r_zet_cookie.zscan(cookies_nnqc)[1])
        dicts = json.loads(cookies_dict[0])
        phonenum = cookies_dict[1]
        print("牛牛汽车每次请求时候的手机号：{phonenum}, cookie:{cookie}".format(phonenum=phonenum, cookie=dicts))
        return dicts



    def start_requests(self):
        self.i+=1
        print("请求总数", self.i)
        request = Request(url=self.start_urls[1], callback=self.parse,)# dont_filter=True)#headers=self.get_headers(),)# cookies=self.get_cookie(""))#,meta={'proxy':self.get_proxy()})
        # 存放url
        request.meta['url_redis'] = url_redis
        # 存放cookie
        request.meta['cookies_redis'] = cookies_nnqc
        # 存放不能用的cookie
        request.meta['useless_cookies'] = unuseless_cookies_nnqc
        request.meta['handle_httpstatus_list'] = [302]
        yield request

    # 所有的汽车品牌列表页
    def parse(self, response):
        self.i += 1
        print("请求总数", self.i)
        cookie = response.headers.getlist('Set-Cookie')
        base_div = response.xpath('//div[@class="listing-brands"]/div[@class="item"]/div[@class="brands"]//div[@class="brand"]')
        cookie_dicts = self.get_cookie(cookie)
        for base_xpath in base_div:
            url = base_xpath.xpath('./a/@href').extract_first()
            brand = base_xpath.xpath('./a/text()').extract_first()
            request = response.follow(url=self.start_urls[0][:-1]+url, cookies=cookie_dicts, callback=self.config_parse,)# dont_filter=True)#headers=self.get_headers())
            request.meta['brand'] = brand

            # 存放url
            request.meta['url_redis'] = url_redis
            # 存放cookie
            request.meta['cookies_redis'] = cookies_nnqc
            # 存放不能用的cookie
            request.meta['useless_cookies'] = unuseless_cookies_nnqc
            request.meta['handle_httpstatus_list'] = [302]
            yield request


    # 带车型选择的详情页
    def config_parse(self, response):
        self.i += 1
        print("请求总数", self.i)
        cookie = response.headers.getlist('Set-Cookie')
        type_lable_div = response.xpath('//ul[@class="tab-content"]/li')
        for div in type_lable_div:
            table_lable = div.xpath('./div[@class="col-sm-3"]/text()').extract_first()
            type_div = div.xpath('./div[@class="col-sm-9"]')
            for li in type_div:
                car_type = li.xpath('.//div/a/text()').extract_first()
                car_type_url = li.xpath('.//div/a/@href').extract_first()
                # 这个是要抓取页的url， 需要去重
                request = response.follow(url=car_type_url, callback=self.parse_select_cartype,)#headers=self.get_headers())#, cookies=self.get_cookie(cookie))
                request.meta['table_lable'] = table_lable
                request.meta['car_type'] = car_type
                request.meta['brand'] = response.meta['brand']

                # 存放url
                request.meta['url_redis'] = url_redis
                # 存放cookie
                request.meta['cookies_redis'] = cookies_nnqc
                # 存放不能用的cookie
                request.meta['useless_cookies'] = unuseless_cookies_nnqc
                request.meta['handle_httpstatus_list'] = [302]
                yield request

    # 所有二级车型页
    def parse_select_cartype(self, response):
        self.i += 1
        print("请求总数", self.i)
        cookie = response.headers.getlist('Set-Cookie')


        # 如果a 连接中有下一页信息则请求下一页
        # 这里分情况，当是第一页时构建从第二页到最后一页的请求， 如果不是第一页则跳过
        isfirstpage = response.xpath('//div[@class="section-pagination"]//span[@class="page current"]/text()').extract_first()
        lastpage = response.xpath('//div[@class="section-pagination"]//span[@class="last"]/a/@href').extract_first()

        print("详情页的页码信息", isfirstpage, lastpage)
        if isfirstpage and lastpage:
            isfirstpage = isfirstpage.strip()
            lastpage_url = lastpage.split('page=')[0]
            lastpage_pagenum = lastpage.split('page=')[1]
            if isfirstpage == "1":
                pageurl = response.url + "&page=%s"
                for pagenum in range(2, int(lastpage_pagenum)+1):
                    nextpage_url = self.start_urls[0] + lastpage_url +"&page=%s"%pagenum
                    # self.selflog.logger.info("继续请求下一页信息:%s" % nextpage_url)
                    request_nextpage = response.follow(url=nextpage_url, callback=self.parse_select_cartype, )#headers=self.get_headers())
                    # 存放url
                    request_nextpage.meta['url_redis'] = url_redis
                    # 存放cookie
                    request_nextpage.meta['cookies_redis'] = cookies_nnqc
                    # 存放不能用的cookie
                    request_nextpage.meta['useless_cookies'] = unuseless_cookies_nnqc
                    request_nextpage.meta['handle_httpstatus_list'] = [302]
                    request_nextpage.meta['table_lable'] = response.meta['table_lable']
                    request_nextpage.meta['brand'] = response.meta['brand']
                    request_nextpage.meta['car_type'] = response.meta['car_type']
                    yield request_nextpage

        type_label = response.meta['table_lable']
        # 车型
        base_car_style = response.xpath('//div[@class="item"]')
        requesturl = response.url

        for div in base_car_style:

            car_style = div.xpath('./div[@class="car-title"]/a/text()').extract_first()
            # 类型去空格处理后使用一个空格隔开
            car_style = deal_style(car_style)
            # 配置没有为空
            # config = li.xpath('./p[@class="c2"]/text()').extract_first()
            config = None

            # 排量
            displacement = deal_displacement(car_style, self)
            # 年款
            year = deal_year(car_style, self)

            # 进口方式
            version = div.xpath('./div[@class="car-subtitle clearfix"]/span/text()').extract_first()
            # 平行进口处理
            if "平行进口" in type_label:
                if USA in version or "美规" in version:
                    version_num = 2
                elif Canada in version:
                    version_num = 3
                elif Mexico in version or "墨西哥版" in version:
                    version_num = 4
                elif European in version:
                    version_num = 5
                else:
                    version_num = "平行None"
            # 进口处理
            elif "进口" in type_label:
                version_num = 1
            # 中规处理
            else:
                if China in version or "国产" in version:
                    version_num = 0
                elif ChinaImport in version:
                    version_num = 1
                else:
                    self.selflog.logger.info("车型{car_style}的进口版本不在规定内".format(car_style=car_style))
                    version_num = None

            # 指导价: 指导价:25.27万下20点
            guide_price = div.xpath('./div/div[@class="car-guide-price"]/text()').extract_first()
            guide_price = deal_guideprice(guide_price,car_style,self)
            price = div.xpath('./div/div[@class="car-price"]/text()').extract_first()
            # 成交量： 车源成交量：3单
            volume = div.xpath('./div[@class="user-info clearfix"]/span[3]/text()').extract_first()
            if volume:
                search_volume = re.search("\d+", volume)
                if search_volume:
                    volume = search_volume.group()

            # 更新时间和详情页url
            detail_url = div.xpath('./div[@class="car-title"]/a/@href').extract_first()
            if detail_url:
                detail_url = self.start_urls[0] + detail_url
            else:
                detail_url = ""

            updatetime = div.xpath('./div[@class="user-info clearfix"]/div[@class="car-publish-time"]/text()').extract_first()
            if updatetime:
                # 更换成统一格式 05-24
                if "/" in updatetime:
                    updatetime_change = "-".join(updatetime.split('/'))
                    updatetime = str(datetime.datetime.now().year) + "-"+ updatetime_change +" 00:00"
                elif ":" in updatetime:
                    updatetime = datetime.datetime.now().strftime('%Y-%m-%d') + " " + updatetime
            else:
                updatetime = ""

            carstyleitem = CarStyleItem()
            carstyleitem['brand'] = response.meta['brand']
            carstyleitem["type"] = response.meta['car_type']
            carstyleitem['year'] = year
            carstyleitem['style'] = car_style
            carstyleitem["requesturl"] = requesturl
            carstyleitem['configuration'] = str(config)
            carstyleitem['displacement'] = displacement
            carstyleitem['version'] = str(version_num)
            carstyleitem['guide_price'] = guide_price
            carstyleitem['price'] = price
            carstyleitem['volume'] = volume
            carstyleitem['status'] = "None"
            carstyleitem['platform'] = 2
            carstyleitem['rediskey'] = url_redis
            carstyleitem['detail_url'] = detail_url
            carstyleitem['updatetime'] = updatetime
            yield carstyleitem

        set_url_r.sadd(url_redis_nnqc, response.url)


