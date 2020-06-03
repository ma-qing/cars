# -*- coding: utf-8 -*-
import datetime
import json
import re

import requests
import scrapy
from fake_useragent import UserAgent
from scrapy import Request

from cars.CONSTANT import China, USA, Canada, European, Mexico
from cars.items import CarStyleItem
from cars.log_utils import SelfLog
from cars.utils import deal_style, deal_year, deal_displacement, deal_guideprice, sav_item, set_redis, Mysqlpython

cookie_r = set_redis(2)
# type_r = set_redis()
dbhelper = Mysqlpython()

cookies_chezhen = "cookies_chezhen"
unuseless_cookies_chezhen = "unuseless_cookies_chezhen"
url_redis = "chezhen"


class ChezhenSpider(scrapy.Spider):
    name = 'chezhen'
    selflog = SelfLog(name)

    cookies = {
        "CzcyAutoLogin":"e8y5J709aeW71cl2Iejbo2x2NdT7gc5bOTQ2MTk2LCJpZCI6IjE2MzY4NCIsInRva2VuIjoiZDgyZTdlNTFmOWJiYjUzODljYmM3NTQ1MjNhNWQ2OGIifQO0O0OO0O0O",
    }

    # 查询车进口类型接口
    type_url = "http://www.chezhency.com/Home/ncar/gettype?cat_id=%s"
    # 车型详情列表页的url
    detail_requesturl = "http://www.chezhency.com/Home/ncar/index/cat_id/{catid}/type_id/{versionkey}/timer/2.html"
    allowed_domains = ['www.chezhency.com']
    start_urls = ['http://www.chezhency.com/', "http://www.chezhency.com/home/index/indexbei.html"]

    # 构造请求头
    def get_headers(self):
        sql = "select ua from useragent order by rand() limit 1;"
        headers = {
            # "User-Agent": dbhelper.readall(sql)[0][0],
            "User-Agent": UserAgent().random,
        }
        return headers

    # # 构造cookie
    # def get_cookies(self, lastcookie):
    #
    #     cookie = json.loads(cookie_r.srandmember("cookies_168"))
    #     while cookie == lastcookie:
    #         cookie = json.loads(cookie_r.srandmember("cookies_168"))
    #     return cookie

    # 构造第一个请求
    def start_requests(self):
        url = self.start_urls[1]
        request = Request(url=url, callback=self.parse_brand, headers=self.get_headers())#, cookies=self.cookies)
        # 存放url
        request.meta['url_redis'] = url_redis
        # 存放cookie
        request.meta['cookies_redis'] = cookies_chezhen
        # 存放不能用的cookie
        request.meta['useless_cookies'] = unuseless_cookies_chezhen
        yield request

    def parse_brand(self, response):
        brand_base = response.xpath("//dl/dd/a")
        for brand in brand_base:
            brandname = brand.xpath('./text()').extract_first()
            url = brand.xpath('./@href').extract_first()
            request = response.follow(url=url, callback=self.parse_type, headers=self.get_headers())#, cookies=self.cookies)
            request.meta['brand'] = brandname
            # 存放url
            request.meta['url_redis'] = url_redis
            # 存放cookie
            request.meta['cookies_redis'] = cookies_chezhen
            # 存放不能用的cookie
            request.meta['useless_cookies'] = unuseless_cookies_chezhen
            yield request

    def parse_type(self, response):
        car_type_dd = response.xpath('//dl[@class="listdl"]/dd')
        for dd in car_type_dd:
            car_type = dd.xpath('./text()').extract_first()
            car_type_id = dd.xpath('./@data-id').extract_first()
            request_url = self.type_url%car_type_id
            result = requests.get(request_url, headers=self.get_headers())
            version_data = eval(result.text).get('data')
            if len(version_data):
                for version in version_data:
                    key = version.get("key")
                    value = version.get('value')
                    detail_url = self.detail_requesturl.format(catid=car_type_id, versionkey=key)
                    request = Request(url=detail_url, callback=self.parse_detail, headers=self.get_headers())# , cookies=self.cookies)
                    request.meta['brand'] = response.meta['brand']
                    request.meta['type'] = car_type
                    request.meta['cartypeid'] = car_type_id
                    request.meta['versionkey'] = key

                    # 存放url
                    request.meta['url_redis'] = url_redis
                    # 存放cookie
                    request.meta['cookies_redis'] = cookies_chezhen
                    # 存放不能用的cookie
                    request.meta['useless_cookies'] = unuseless_cookies_chezhen
                    yield request

    #车型详情信息列表页
    def parse_detail(self, response):
        brand = response.meta['brand']
        cartype = response.meta['type']
        # 当请求下一页时候注意加上这条数据
        cartypeid = response.meta['cartypeid']
        versionkey = response.meta['versionkey']

        # li-data数据解析
        base_xpath = response.xpath('//ul[@class="carlist"]/li')
        requesturl = response.url
        for li in base_xpath:
            carstyle = li.xpath('./a/div[@class="c_title"]/p[@class="lt"]/text()').extract_first()
            price = li.xpath('./a/div[@class="c_title"]/p[@class="rt"]/text()').extract_first()
            version = li.xpath('./a/div[@class="detail"]/p[@class="lt"]/text()').extract_first()
            guide_price = li.xpath('./a/div[@class="detail"]/p[@class="rt"]/text()').extract_first()
            config = li.xpath('./a/div[@class="intro"][2]/text()').extract_first()

            if carstyle:
                carstyle = deal_style(carstyle)
            else:
                carstyle = ""
            year = deal_year(carstyle, self)

            # 排量
            displacement = deal_displacement(carstyle, self)
            # 指导价格
            if guide_price:
                guide_price = deal_guideprice(guide_price)

            # 详情页P标签中的值判断进口版本
            if China in version:
                if "进口" in carstyle:
                    version_num = 1
                else:
                    version_num = 0
            elif USA in version:
                version_num = 2
            elif Canada in version:
                version_num = 3
            elif Mexico in version:
                version_num = 4
            elif European in version:
                version_num = 5
            else:
                version_num = "平行None"

            updatetime = li.xpath('./a/div[@class="attach"]/p[@class="rt"]/text()').extract_first()
            if updatetime:
                if "-" in updatetime:
                    updatetime = str(datetime.datetime.now().year) + "-"+ updatetime +" 00:00"
                elif ":" in updatetime:
                    updatetime = datetime.datetime.now().strftime('%Y-%m-%d') + " " + updatetime
            else:
                updatetime = ""

            detail_url = li.xpath('./a/@href').extract_first()
            if detail_url:
                detail_url = self.start_urls[0]+detail_url
            else:
                detail_url = ""

            get_item = sav_item(brand=brand,
                            cartype=cartype,
                            year=year,
                            carstyle=carstyle,
                            guide_price=guide_price,
                            displacement=displacement,
                            config=config,
                            version_num =version_num,
                            price=price,
                            volume=None,
                            platform=3,
                            requesturl=detail_url,
                            rediskey=url_redis,
                            updatetime=updatetime)
            yield get_item
        # 懒加载请求最后一条数据
        lastid = response.xpath('//ul[@class="carlist"]/li[last()]/@data-id').extract_first()
        if lastid:
            request_url = self.detail_requesturl.format(catid=cartypeid, versionkey=versionkey)+"?id={lastid}".format( lastid=lastid)
            request = response.follow(url=request_url, callback=self.parse_detail, headers=self.get_headers())# , cookies=self.cookies)
            # 添加request meta信息
            # 当请求下一页时候注意加上这些数据
            request.meta['brand'] = brand
            request.meta['type'] = cartype
            request.meta['cartypeid'] = cartypeid
            request.meta['versionkey'] = versionkey
            # 存放url
            request.meta['url_redis'] = url_redis
            # 存放cookie
            request.meta['cookies_redis'] = cookies_chezhen
            # 存放不能用的cookie
            request.meta['useless_cookies'] = unuseless_cookies_chezhen
            # self.selflog.logger.info("继续抓取下一页信息:{}".format(request_url))
            yield request













