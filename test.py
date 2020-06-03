'''
zadd
zrange 0 -1 # 所有元素    withscores  查看所有元素，并且还有对应的得分值
# 返回成员的分数值
ZSCORE key member
# 移除一个或者多个成员
ZREM key member
# 返回指定成员的索引
ZRANK key member
# 获取成员数量
ZCARD key

'''
import datetime
import json
import os
import random
import re

import  redis
import requests
from lxml import etree
from cars.utils import set_redis

# r = set_redis(2)

dicts = {
        "_niu_niu_session":"RkQvVFo4V3dLLzFvTUNLcVdERlZ0WHpzMitocmNXRXlCUDdBL2JNbTcwdXJINFhWcmh2N1NSaGJZbnkvelZvUmpZZjlxQmxxTDZDNzUvd1l6T2VYUzl2eFhKU2x0UWF6by9rUzExdnFYR0w1akFaN1ZIMkZVY2dQZEJ0SDhqL001elpyNVhmSWVOVmZSVnNHbXl3YUpoaXpMWFdQZHFLWUtFMFRGZVpxcmJsWUlHcFUvdkt1ZkxnWnlLcm9LTWUxNHl0em9YeDR6N3ZrSnRMbUZMNHBvTjRBR29PWTBsWWYxaTV0bjBYZ3ZhWi9QMmo3WVV5RkJYeS9zbjhjUVZEQjVkbHhrUTN1cXd1bmlsVjg0QWhJL1FTTktOU1NiYTI3Ri9sMFNEMVd4RFdNTHhWMzFkdmVhQzZnb0l6dHBpa1I4Tjd2RkViYW02UmNoaGRib0hhaVVMMTJZY0prMitSekdqZlBzY0dIL2lFPS0tYzB1TXpSYkVodGtaQlpKeEpmWkkxUT09--c5f37dcd254956525bf8283c40b188f569b54739",

    }

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    "Cookie":"_niu_niu_session=dWo3cU1QQUN2YUpsUkVJVzBRV09BVGIzUno5bmlOejQzYmViV1pTSDJvZHJBVkk3T2tsSEg3SDFwNmZaU1pzbnMyTWVhQ095cXRmMm5kaEhyNjdqNzhGYVZxei85LzZqaHgzTnlKelMzWTJJMzgrcHRmaHNrbS9wNG5hN1c0aDJTZDVUdlBKczBrRTVnalJXUFdycEtEeThxNzZrblplOGxBQjNzL05HT21JZDNSRHZCemZueFFRYldOSHQ4MllySXJpRE81ZzVlMG1vcm5pUm9XY2h5NlVkeXQreHE1ZjcyS1VvSno0ZEkyVHlqTU85bkZMbDR3dGw0QndWakpDNVNSRXA3eFRCY3BNLzYzMjFPN0lLVHpKd0RUZ09WZmZXbDJWeHVTc1BSOTlBWnNQdEdrWFJENWFSMXN3bWNITjlGOTM1Um81ZnNtOWtyaUU5WW1GVjU2akNxa1hqR2NMQUhsdldkMUJwYkhRPS0tMk9KUjBJOXlQYytCREJkKzdkL0E2UT09--f9524959fa03db10932b17fb4c5b21b1077cbbf2",
}
url = "http://www.niuniuqiche.com/v2/sell_cars?brand_name=%E5%A5%A5%E8%BF%AA&car_model_name=%E5%A5%A5%E8%BF%AAA3&firm_name=%E4%B8%80%E6%B1%BD-%E5%A4%A7%E4%BC%97%E5%A5%A5%E8%BF%AA"
# url = "http://www.chehang168.com/index.php?c=index&m=index"
# result = requests.get(url, headers=headers)
# tree = etree.HTML(result.text)
# print("****"+tree.xpath('//div[@class="section-pagination"]//span[@class="page current"]/text()')[0].strip()+"*****")
# print("****"+tree.xpath('//div[@class="section-pagination"]//span[@class="last"]/a/@href')[0].split('page=')[1]+"*****")


# for i in r.zscan("test")[1]:
#     mapping = {}
#     mapping[i[0]] = i[1]
#     r.zadd("cookies_car168", mapping)


# dictss = {
#         "CzcyAutoLogin":"e8y5J709aeW71cl2Iejbo2x2NdT7gc5bOTQ2MTk2LCJpZCI6IjE2MzY4NCIsInRva2VuIjoiZDgyZTdlNTFmOWJiYjUzODljYmM3NTQ1MjNhNWQ2OGIifQO0O0OO0O0O",
#     }

# r = set_redis(2)
# for i in r.zscan("unuseless_cookies_car168")[1]:
#     mapping = {}
#     mapping[i[0]] = i[1]
#     print(mapping)
#     r.zadd("cookies_car168", mapping)

str1 = "【车行168】您的验证码是6843，10分钟内有效，请勿泄漏给他人"
str2 = "验证码为7474"
print(re.search("验证码.?(\d+)", str2).group(1))

