# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class CarStyleItem(scrapy.Item):
    table_name = "car_style"
    # 存入redis中的信息
    requesturl = Field()
    rediskey = Field()

    brand = Field()
    type = Field()
    year = Field()
    style = Field()
    guide_price = Field()
    displacement = Field()
    configuration = Field()
    version = Field()
    status = Field()


    # 另一个表里的保存信息
    price = Field()
    volume = Field()
    platform = Field()
    detail_url = Field()
    updatetime = Field()


class CarDetailItem(scrapy.Item):
    table_name = "car_detail"
    platform = Field()
    vehicleType = Field()
    price = Field()
    volume = Field()
    detail_url = Field()
    updatetime = Field()


