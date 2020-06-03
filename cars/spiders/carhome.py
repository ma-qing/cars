# -*- coding: utf-8 -*-
import re
import string

import scrapy
from scrapy import Request


class CarhomeSpider(scrapy.Spider):
    name = 'carhome'
    allowed_domains = ['autohome.com.cn']
    start_urls = ['http://autohome.com.cn/', "https://www.autohome.com.cn/grade/carhtml/%s.html"]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
        'Cache-Control': "no-cache",
    }

    def start_requests(self):
        url = self.start_urls[1]
        for i in 'A':#string.ascii_uppercase:
            request = Request(url=url % i, callback=self.parse_brand, headers=self.headers)
            # self._monkey_patching_HTTPClientParser_statusReceived()
            yield request

    # 标注进口信息
    def parse_brand(self, response):
        base_dl = response.xpath('//dl')
        for dl in base_dl:
            brand = dl.xpath('./dt/div/a/text()').extract_first()
            type_url = dl.xpath('./dd/ul/li/h4/a/@href').extract_first()
            type_url_request = response.follow(url=type_url, callback=self.parse_all_esay, headers=self.headers)
            type_url_request.meta['brand'] = brand
            # 是否进口
            version = response.xpath('//div[@class="h3-tit"]/a/text()').extract_first()
            if "进口" in version:
                pass
            else:
                pass

            yield type_url_request

    def parse_all_esay(self, response):
        esay_div = response.xpath('//div[@class="name-param"]')
        # 车型
        car_type = response.xpath('//div[@class="athm-title__name athm-title__name--blue"]/a/text()').extract_first()

        for div in esay_div:
            detail_url = div.xpath('./p/a/@href').extract_first()
            config = div.xpath('./p[2]/span/text()').extract()

            detail_url_request = response.follow(url=detail_url, callback=self.parse_detail_onsell,
                                                 headers=self.headers)
            detail_url_request.meta['brand'] = response.meta['brand']
            detail_url_request.meta['config'] = config
            detail_url_request.meta['cartype'] = car_type
            yield detail_url_request

    # 在售款
    def parse_detail_onsell(self, response):
        brand = response.meta['brand']
        config = response.meta['config']
        car_type = response.meta['cartype']
        car_style = response.xpath('//div[@class="information-tit"]/h2/text()').extract_first()
        pailiang = response.xpath('//div[@class="param-list"]/div[2]/p/text()').extract_first()
        search_year = re.search("\d+款", car_style, re.I)
        if search_year:
            year = search_year.group()
            car_style = "".join(car_style.replace(year, "").split())
        else:
            year = None
        # 插入数据库中
        

    # 停售款 使用接口去拿
    def parse_detail_discontinued(self, response):
        pass



