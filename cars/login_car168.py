# coding:utf-8
import json
import random
from time import sleep, time

import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver import ChromeOptions
from cars.madashi import get_code, build_phonenum, get_token, get_phonenum

# projectid = "19503"
from cars.utils import set_redis

projectid = "32409"
matchrule = "验证码.?(\d+)"
phone_num_list = ["16517865849"]#"17169479357""16535511249","16574980930","16531165344","16533431172",]
phone_num = phone_num_list[0]
print("从列表中取得手机号:", phone_num)
# token = get_token('maxfire', "ma123456")
# phone_num_from = get_phonenum(projectid, token=token, phone=phone_num, loop=2)
token, phone_num_from = build_phonenum(projectid, loop=2, phone=phone_num)
print("解码平台手机号:", phone_num_from)

# option = ChromeOptions()
# option.add_experimental_option('excludeSwitches', ['enable-automation'])

def get_driver():
    driver = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")#, options=option)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
      "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    driver.maximize_window()
    sleep(0.5)
    driver.get("http://www.chehang168.com/")
    sleep(1)  # 等待页面加载
    return driver


def get_stacks(distance):
    distance += 20
    '''
        拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速
        变速运动基本公式：
        ① v=v0+at       匀加速\减速运行
        ② s=v0t+½at²    位移
        ③ v²-v0²=2as
     '''
    # 初速度
    v0 = 0
    # 加减速度列表
    a_list = [50, 65, 80]
    # 时间
    t = 0.2
    # 初始位置
    s = 0
    # 向前滑动轨迹
    forward_stacks = []
    mid = distance * 3 / 5
    while s < distance:
        if s < mid:
            a = a_list[random.randint(0, 2)]
        else:
            a = -a_list[random.randint(0, 2)]
        v = v0
        stack = v * t + 0.5 * a * (t ** 2)
        # 每次拿到的位移
        stack = round(stack)
        s += stack
        v0 = v + a * t
        forward_stacks.append(stack)
    # 往后返回20距离，因为之前distance向前多走了20
    back_stacks = [-5, -5, -5, -5,]
    return {'forward_stacks': forward_stacks, 'back_stacks': back_stacks}


def mouseclick():
    import pyautogui
    pyautogui.FAILSAFE = True
    # x = slider.location['x']
    # y = slider.location['y']
    # halfx = slider.size['width']//2
    # halfy = slider.size['height']//2
    # pyautogui.moveTo(x=1296, y=520)
    # pyautogui.dragTo(x=1603, y=516, duration=1)
    pyautogui.moveTo(x=1229, y=403)
    pyautogui.dragTo(x=1476, y=405, duration=1)


def clicklogin(driver, phone_num, projectid, token, matchrule):
    # 手机号页面
    phone_input = driver.find_element_by_id("uname")
    phone_input.send_keys(phone_num)
    # 点击获取验证码
    sendcode = driver.find_element_by_id("sendCode")
    sendcode.click()
    # 接收验证码
    code = get_code(projectid, phonenum=phone_num, token=token, matchrule=matchrule)
    if code:
        # 输入验证码
        code_input = driver.find_element_by_id("code")
        code_input.send_keys(code)

        login = driver.find_element_by_id("button")
        login.click()
        sleep(2)
        driver.refresh()
        tbCookies = driver.get_cookies()
        # driver.quit()
        cookies = {}
        for item in tbCookies:
            if item['name'] == "DEVICE_ID" or item['name'] == "U":
                cookies[item['name']] = item['value']
        print(cookies)
        r = set_redis(2)

        mapping = {json.dumps(cookies): int(phone_num)}
        print(mapping)
        r.zadd("cookies_car168", mapping)
        print("成功存入redis")
    else:
        print("没有接收到验证码")


if __name__ == '__main__':
    driver = get_driver()
    sleep(1)
    mouseclick()
    clicklogin(driver, phone_num, projectid, token=token, matchrule=matchrule)





