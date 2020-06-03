# coding:utf-8

# import base64
# from io import BytesIO
# from time import sleep, time
#
# from selenium import webdriver
# phone_num = "17131948031"
# password = "ma123456"
# browser = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
# sleep(0.5)
# browser.get("http://www.niuniuqiche.com/login")
# sleep(2)  # 等待页面加载
# login_xpath = browser.find_element_by_xpath('//ul/li[1]/a')
# sleep(1)
# login_xpath.click()
# sleep(2)
# # # 输入手机号哦和密码
# # phone_input = browser.find_element_by_id("user_mobile")
# # phone_input.send_keys(phone_num)
# # sleep(0.5)
# # password_input = browser.find_element_by_id("user_password")
# # password_input.send_keys(password)
# # sleep(0.5)
# #点击加载验证码
# click_load_picture = browser.find_element_by_xpath('//div[@class="geetest_wait"]')
# click_load_picture.click()
# sleep(2)
#
# # 截图查看验证码
# browser.get_screenshot_as_file(r"./yanzhengtupian.png")
#
#
# def get_images(browser):
#     """
#     获取验证码图片
#     :return: 图片的location信息
#     """
#     sleep(1)
#     # browser.web_driver_wait_ruishu(10, "class", 'geetest_canvas_slice')
#     fullgb = browser.execute_script('document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL("image/png")')["value"]
#     bg = browser.execute_script('document.getElementsByClassName("geetest_canvas_fullbg geetest_fade geetest_absolute")[0].toDataURL("image/png")')["value"]
#     return bg, fullgb
#
#
# print(get_images(browser))
# # def get_decode_image(self, filename, location_list):
# #     """
# #     解码base64数据
# #     """
# #     _, img = location_list.split(",")
# #     img = base64.decodebytes(img.encode())
# #     new_im: image.Image = image.open(BytesIO(img))
# #     return new_im
#
#
# # browser.close()
import random
import time
from time import sleep
from urllib import parse

from lxml import etree


import requests
from selenium import webdriver
# driver = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
phonenum = "16573973446"
password = "ma123456"

# 牛牛汽车的登录url
signin_nnqc_url = "http://www.niuniuqiche.com/v2/users/sign_in"
# 牛牛汽车的注册url
signup_nnqc_url = "http://www.niuniuqiche.com/v2/users/sign_up"
send_sucess = "success"
send_agin = "您的短信已发送,请勿重复提交"
registered = ""
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    }



def signin(siginurl, s):
    # user = {}
    data = {
        "user[mobile]": "16601223912",
        "user[password]": "ma123456",
        "user[remember_me]": 0,
    }

    result = s.post(url=siginurl, data=data, headers=headers)
    print(result.headers.get("Set-Cookie"))
    # print(result.text)


def signup(s, phonenum, code, password, realname, authtoken):
    province_dict = {
        "698": "台湾",
        "393": "辽宁省",
        "425": "山东省",
        "273": "湖南省",
        "32": "福建省",
        "56": "甘肃省",
        "73": "广东省",
        "118": "贵州省",
        "132": "河北省",
        "166": "黑龙江省",
        "197": "河南省",
        "236": "湖北省",
        "303": "吉林省",
        "332": "江西省",
        "474": "陕西省",
        "488": "山西省",
        "1": "北京",
        "3": "天津",
        "5": "上海",
        "7": "重庆",
        "9": "安徽省",
        "511": "四川省",
        "544": "云南省",
        "596": "青海省",
        "600": "海南省",
        "609": "广西",
        "631": "内蒙古",
        "652": "宁夏",
        "660": "西藏",
        "663": "新疆",
        "562": "浙江省",
        "687": "香港",
        "689": "澳门",
    }
    area_url = "http://www.niuniuqiche.com/v2/ajax/areas/%s"
    province_id = random.choice(list(province_dict.keys()))
    area_dict = s.get(area_url %province_id, headers=headers)
    areas = eval(area_dict.text).get('data').get('cities')
    area_id = random.choice(areas)[1]

    url = "http://www.niuniuqiche.com/v2/users"
    dicts = {
        "authenticity_token": authtoken,
        "referer": "http://www.niuniuqiche.com/v2/users/sign_in",
        "user[mobile]": phonenum,
        "valid_code": code,
        "type": 0,
        "user[password]": password,
        "user[password_confirmation]": password,
        "user[name]": realname,
        "user[company]": "暂无公司",
        "province": province_id,
        "user[area_id]": area_id,
    }
    print("注册时候发送参数为：", dicts)
    signup_headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
        "Referer": "http://www.niuniuqiche.com/v2/users/sign_up",
        "Origin": "http://www.niuniuqiche.com",
        "Host": "www.niuniuqiche.com",
        "X-CSRF-Token": authtoken,
        "X-Requested-With": "XMLHttpRequest",
    }

    result = s.post(url=url, data=parse.urlencode(dicts), headers=signup_headers, verify=False)
    return result.status_code, result.headers, result.text


def get_auth():
    url = signup_nnqc_url
    s = requests.Session()
    result = s.get(url, headers=headers).text
    tree = etree.HTML(result)
    authentoken = tree.xpath('//head/meta[@name="csrf-token"]/@content')[0]
    request_code = tree.xpath('//head/script/text()')[0].split(';')[1][-13:-1]

    return s, authentoken, request_code





# 15201286837
# ma123456
if __name__ == '__main__':
    # check_isignup(phonenum)
    # signin(siginurl=signin_nnqc_url)
    # ls1 = ["ll", "22"]
    pass