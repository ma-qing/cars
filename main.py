# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 根据项目配置获取 CrawlerProcess 实例
process = CrawlerProcess(get_project_settings())

# 添加需要执行的爬虫
process.crawl('nnqc')
process.crawl('car168')
process.crawl('chezhen')

# 执行
process.start()


# process.crawl('dining', dt='20191119')
# # 如果向爬虫传递参数
# class Dining(scrapy.Spider):
#     name = 'dining'
#
#     def __init__(self, dt)
#         self.dt = dt