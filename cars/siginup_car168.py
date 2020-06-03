# # -*- coding: utf-8 -*-
'''
牛牛汽车：10s 两个并发， 10分钟 40个请求被封
'''
import random
import time

import requests
from selenium.webdriver.support.ui import WebDriverWait
from appium import webdriver

from cars.madashi import build_phonenum, get_code, relase_phonenum, get_token

desired_caps = {}
desired_caps['platformName'] = 'Android'
desired_caps['deviceName'] = '127.0.0.1:62001'
desired_caps['platformVersion'] = '5.1.1'
desired_caps['appPackage'] = 'com.zjw.chehang168'
desired_caps['appActivity'] = 'com.zjw.chehang168.V40MainActivity'
desired_caps['noReset'] = True

# 接码平台相关数据
# projectid = "19503"
projectid = "32409"
matchrule = "验证码.?(\d+)"
carnames =["松志汽车公司","卓尔汽车公司","展立汽车公司","星季汽车公司","板芙汽车公司","华阳宇光汽车公司","华鑫重汽车公司","铭轩汽车公司","恒大汽车公司","亿德汽车公司","宏伟汽车公司","华信汽车公司","宝仕尼汽车公司","名威汽车公司","盛联汽车公司","久通汽车公司","强盛汽车公司","鑫江汽车公司","运鹏汽车公司","赛维思汽车公司","申仕汽车公司","广源汽车公司","常益行汽车公司","万里阳光汽车公司","依维柯汽车公司","仁合汽车公司","大洋汽车公司","鸿泽汽车公司","火花汽车公司","诚功汽车公司","慧通汽车公司","诺士汽车公司","凯盛汽车公司","同德利汽车公司","瑞宸汽车公司","科尔汽车公司","火焰驹汽车公司","杰爱必汽车公司","飞龙腾达汽车公司","惠华汽车公司","建荣汽车公司","邱隘钧达汽车公司","拓远汽车公司","宝盛汽车公司","玉辉汽车公司","坤诺汽车公司","江南汽车公司","利富得汽车公司","晨俊汽车公司","欧纯汽车公司","万豪汽车公司","盼耀汽车公司","戈尔德汽车公司","华盛汽车公司","康天汽车公司","宏发汽车公司","鸿建汽车公司","美冠汽车公司","强鑫汽车公司","冠洁汽车公司","名毂汇汽车公司","爱瑞德汽车公司","金德利汽车公司","华夏汽车公司","云良汽车公司","海赛汽车公司","振高汽车公司","兰博汽车公司","强玻汽车公司","车霸汽车公司","盛安汽车公司","恒发汽车公司","鹏达跃虎汽车公司","迪恩杰汽车公司","浩鑫汽车公司","欧迪汽车公司","天誉汽车公司","庆合汽车公司","瑞祥汽车公司","康特汽车公司","纳罗多汽车公司","同得利汽车公司","宜美汽车公司","海跃汽车公司","弘祥汽车公司","华川汽车公司","博诚金龙汽车公司","杭策汽车公司","弘卓汽车公司","力挺汽车公司","汇宝汽车公司","云都汽车公司","星火汽车公司","韩瑞麟汽车公司","环瑞汽车公司","酷卡汽车公司","鸿胜汽车公司","伟亿科汽车公司","倍利汽车公司","龙威旺汽车公司","绿劲汽车公司","利群汽车公司","多思达汽车公司","通运汽车公司","雅尔普汽车公司","金逸汽车公司","卓迅汽车公司","宇凯世华汽车公司","博众奥达汽车公司","正洪汽车公司","实达汽车公司","铖驰圣汽车公司","星缘汽车公司","恒达汽车公司","驰耐特汽车公司","畅博汽车公司","莱斯康汽车公司","鸿宇汽车公司","新力达汽车公司","中鑫汽车公司","凯华汽车公司","同创思特汽车公司","佳诚汽车公司","荣林汽车公司","科耐泰汽车公司","五龙汽车公司","永余汽车公司","奥展汽车公司"]
name_list = ["裴玉", "陈英", "赵兵", "9442", "戴国强", "陶洪万", "朱洪纯", "徐亚玲", "徐宗玲", "刘海琪", "曾辉", "唐转兵", "黄飞", "光光", "谢林华", "梁远述",
             "王波香", "王洪超", "刘江", "黄光平", "赵磊", "杨春香", "卢军", "谭恢来", "徐福海", "陈群华", "敬小玲", "王柏杨", "刘崇溶", "袁微", "冯世军", "袁舒含",
             "李贵君", "袁绍斌", "李定其", "罗江山", "王广芳", "孔宪全", "曹兴富", "游伟", "宁有洁", "陈桂香", "王恒英", "吴文模", "叶元凤", "陈德民", "樊艳林",
             "赵斌", "罗宏", "胡支陶", "胡支炎", "张伟", "丛占国", "赵一航", "徐子程", "傅长远", "赵秀宇", "王海龙", "张涛", "姜雪娜", "冷忠仁", "曹松", "张云",
             "丁伟深", "殷梓", "吴锦", "董文欣", "缪杰", "何慧", "吴明", "黄仁鹤", "陈锵", "谢中", "刘勇", "蒋周宁", "陈忠", ]

def get_driver():
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    return driver

def get_size(driver):
    x = driver.get_window_size()['width']
    y = driver.get_window_size()['height']
    return (x, y)


from appium.webdriver.common.touch_action import TouchAction

def touch_test(driver, start, end, el):
    actions = TouchAction(driver)
    actions.long_press(el) # 类似手指按压屏幕的(100, 300)位置
    actions.wait()
    actions.move_to(x=end[0], y=end[1]) # 移动手指到达(100, 100)位置
    actions.release() # 放开手指
    actions.perform() # 将上面3个操作串联起来，依次执行



# 跳过id
def logincar168(driver):
    try:
        # 等待3s看跳过界面是否出现
        if WebDriverWait(driver, 3).until(lambda x: x.find_element_by_xpath("//android.widget.Button[@resource-id='com.zjw.chehang168:id/itemButton']")):
            driver.find_element_by_xpath("//android.widget.Button[@resource-id='com.zjw.chehang168:id/itemButton']").click()
    except Exception as e:
        print(e)

    try:
        # 使用账号名密码登录
        if WebDriverWait(driver, 3).until(lambda x: x.find_element_by_xpath("//android.widget.TextView[@resource-id='com.zjw.chehang168:id/regButton']")):
            driver.find_element_by_xpath("//android.widget.TextView[@resource-id='com.zjw.chehang168:id/regButton']").click()
    except Exception as e:
        print(e)

    try:
        # 输入手机号
        if WebDriverWait(driver, 3).until(lambda x: x.find_element_by_xpath("//android.widget.EditText[@resource-id='com.zjw.chehang168:id/unameEdit']")):
            driver.find_element_by_xpath("//android.widget.EditText[@resource-id='com.zjw.chehang168:id/unameEdit']").send_keys('16573973452')
            driver.find_element_by_xpath("//android.widget.EditText[@resource-id='com.zjw.chehang168:id/pwdEdit']").send_keys('ma123456')
            driver.find_element_by_xpath("//android.widget.Button[@resource-id='com.zjw.chehang168:id/loginButton']").click()
    except Exception as e:
        print(e)
    try:
        # 安全验证
        if WebDriverWait(driver, 8).until(lambda x: x.find_element_by_xpath(
                "//android.view.View[@resource-id='nc_1_n1t']")):
            inter = driver.find_element_by_xpath(
                "//android.view.View[@resource-id='nc_1_n1t']")
            wrapper = driver.find_element_by_xpath(
                "//android.view.View[@text='请向右滑动验证']")
            print(inter.location, inter.size)

            start = [inter.location['x']+inter.size["width"]//2, inter.location['y']+inter.size["height"]//2]
            end = [wrapper.location['x']+wrapper.size["width"]-inter.size["width"]//2, inter.location['y']+inter.size["width"]//2]
            # end = [670, 0]
            print(start,end)
            touch_test(driver=driver, start=start, end=end, el=inter)
    except Exception as e:
        print(e)
    try:
        if WebDriverWait(driver, 3).until(lambda x: x.find_element_by_xpath("//android.widget.ImageView[@resource-id='com.zjw.chehang168:id/iv_argee']")):
            # 勾选统一协议
            driver.find_element_by_xpath("//android.widget.ImageView[@resource-id='com.zjw.chehang168:id/iv_argee']").click()
            # 点击确定
            driver.find_element_by_xpath("//android.widget.Button[@resource-id='com.zjw.chehang168:id/btn_know']").click()
    except Exception as e:
        print(e)


# 注册
def signup_car168(driver):
    try:
        # 等待3s看跳过界面是否出现
        if WebDriverWait(driver, 2).until(lambda x: x.find_element_by_xpath("//android.widget.Button[@resource-id='com.zjw.chehang168:id/itemButton']")):
            driver.find_element_by_xpath("//android.widget.Button[@resource-id='com.zjw.chehang168:id/itemButton']").click()
    except Exception as e:
        print(e)

    # 接码平台接口拿到的token，手机号
    token, phone_nume = build_phonenum(projectid, loop=2, filter='')
    try:
        # 输入手机号
        if WebDriverWait(driver, 3).until(lambda x: x.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/unameEdit']")):
            driver.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/unameEdit']").send_keys(phone_nume)
            # 点击获取验证码按钮
            driver.find_element_by_xpath(
                "//android.widget.TextView[@resource-id='com.zjw.chehang168:id/loginButton']").click()
    except Exception as e:
        print(e)

    try:
        # 安全验证
        if WebDriverWait(driver, 15).until(lambda x: x.find_element_by_xpath(
                "//android.view.View[@resource-id='nc_1_n1t']")):
            inter = driver.find_element_by_xpath(
                "//android.view.View[@resource-id='nc_1_n1t']")
            wrapper = driver.find_element_by_xpath(
                "//android.view.View[@text='请向右滑动验证']")
            print(inter.location, inter.size)

            start = [inter.location['x']+inter.size["width"]//2, inter.location['y']+inter.size["height"]//2]
            end = [wrapper.location['x']+wrapper.size["width"]-inter.size["width"]//2, inter.location['y']+inter.size["width"]//2]
            # end = [670, 0]
            print(start,end)
            touch_test(driver=driver, start=start, end=end, el=inter)
    except Exception as e:
        print(e)

    # 发送验证码接口
    print("手机号", phone_nume)
    code = get_code(projectid=projectid, phonenum=phone_nume, token=token, matchrule=matchrule)
    # code = "1234"
    print("验证码:***{code}***".format(code=code))
    # relase_phonenum(projectid, phone_nume, token)
    if not code:
        print("没有收到验证码，直接退出")
        return None
    try:
        # 输入验证码
        if WebDriverWait(driver, 15).until(lambda x: x.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/tv_0']")):
            x1 = driver.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/tv_0']")
            x1.click()
            x1.send_keys(code[0])
            x2 = driver.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/tv_1']")
            x2.click()
            x2.send_keys(code[1])
            x3 = driver.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/tv_2']")
            x3.click()
            x3.send_keys(code[2])
            x4 = driver.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/tv_3']")
            x4.click()
            x4.send_keys(code[3])
    except Exception as e:
        print(e)


    # 如果有错误提示
    try:
        if WebDriverWait(driver, 1).until(lambda x:x.find_element_by_xpath("//android.widget.TextView[@resource-id='com.zjw.chehang168:id/btn2']")):
            driver.find_element_by_xpath("//android.widget.TextView[@resource-id='com.zjw.chehang168:id/btn2']").click()
            print("验证码错误")
    except Exception as e:
        print("验证通过:", e)

    # 输入个人信息进行注册
    try:
        if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/nameEdit']")):
            # 真实姓名
            driver.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/nameEdit']").send_keys(
                random.choice(name_list))
            # 登录密码
            driver.find_element_by_xpath(
                "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/pwdEdit']").send_keys("ma123456")
            # 工作地点: 点击选择
            driver.find_element_by_xpath(
                "//android.widget.TextView[@resource-id='com.zjw.chehang168:id/areaText']").click()
            choice_driver = driver
            choice_city(choice_driver)
            # 填写公司名
            try:
                if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                        "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/companyEdit']")):
                    driver.find_element_by_xpath(
                        "//android.widget.EditText[@resource-id='com.zjw.chehang168:id/companyEdit']").send_keys(
                        random.choice(carnames))
                    # 选择公司类型
                    driver.find_element_by_xpath("//android.widget.RadioButton[@text='其他']").click()
                    # 勾选同意政策
                    driver.find_element_by_xpath("//android.widget.ImageView[@resource-id='com.zjw.chehang168:id/itemCheckImg']").click()
                    # 完成注册
                    driver.find_element_by_xpath("//android.widget.TextView[@resource-id='com.zjw.chehang168:id/submitButton']").click()
            except Exception as e:
                print("选择城市后没有进行页面跳转", e)
    except Exception as e:
        print("选择公司前出错,", e)
    # 点击我的
    try:
        if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                "//android.widget.RadioButton[@resource-id='com.zjw.chehang168:id/radio_button4']")):
            driver.find_element_by_xpath("//android.widget.RadioButton[@resource-id='com.zjw.chehang168:id/radio_button4']").click()
    except Exception as e:
        print("没有我",e)
    # 点击设置
    try:
        if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                "//android.widget.ImageView[@resource-id='com.zjw.chehang168:id/rightImg']")):
            driver.find_element_by_xpath("//android.widget.ImageView[@resource-id='com.zjw.chehang168:id/rightImg']").click()
    except Exception as e:
        print("没有设置",e)

    # 点击退出登录
    try:
        if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                "//android.widget.TextView[@resource-id='com.zjw.chehang168:id/tv_content' and @text='退出登录']")):
            driver.find_element_by_xpath("//android.widget.TextView[@resource-id='com.zjw.chehang168:id/tv_content' and @text='退出登录']").click()
    except Exception as e:
        print("没有退出登录",e)
    # 点击确认
    try:
        if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                "//android.widget.Button[@resource-id='android:id/button1']")):
            driver.find_element_by_xpath("//android.widget.Button[@resource-id='android:id/button1']").click()
    except Exception as e:
        print("没有确认按钮",e)


def choice_city(driver):
    # 选择省份：福建
    try:
        if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                "//android.widget.ListView[@resource-id='com.zjw.chehang168:id/list1']/android.widget.RelativeLayout[2]/android.widget.ListView[1]/android.widget.RelativeLayout[4]")):
            driver.find_element_by_xpath(
                "//android.widget.ListView[@resource-id='com.zjw.chehang168:id/list1']/android.widget.RelativeLayout[2]/android.widget.ListView[1]/android.widget.RelativeLayout[4]").click()
    except Exception as e:
        print("省份选择出错:", e)
    else:
        # 选择地区：福州
        try:
            if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                    "//android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[2]/android.widget.ListView[1]/android.widget.RelativeLayout[1]/android.widget.TextView[2]")):
                driver.find_element_by_xpath(
                    "//android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[2]/android.widget.ListView[1]/android.widget.RelativeLayout[1]/android.widget.TextView[2]").click()
        except Exception as e:
            print("地区选择出错:", e)
        else:
            # 闽清县
            try:
                if WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath(
                        "//android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[2]/android.widget.RelativeLayout[1]/android.widget.ListView[1]/android.widget.RelativeLayout[5]/android.widget.TextView[1]")):
                    driver.find_element_by_xpath(
                        "//android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[2]/android.widget.RelativeLayout[1]/android.widget.ListView[1]/android.widget.RelativeLayout[5]/android.widget.TextView[1]").click()
            except Exception as e:
                print("城市选择出错:", e)

# 数据
def get_data(driver):
    aodi = driver.find_element_by_xpath("//android.widget.ListView[@resource-id='com.zjw.chehang168:id/carIndexlist']/android.widget.RelativeLayout[5]")
    print(aodi, type(aodi))
    print(aodi.text)
    aodi.click()
    time.sleep(3)
    aodia3 = driver.find_element_by_xpath("//android.widget.TextView[@text='奥迪A3']")
    aodia3.click()
    time.sleep(2)
    all_div = driver.find_element_by_xpath("//android.widget.ListView[@resource-id='com.zjw.chehang168:id/list1']/android.widget.RelativeLayout")
    # "//android.widget.ListView[@resource-id='com.zjw.chehang168:id/list1']/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.LinearLayout[1]"
    # "//android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.view.View[1]/android.widget.RelativeLayout[1]/android.view.View[1]/android.widget.ListView[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.LinearLayout[1]/android.widget.TextView[1]"
    text_div = all_div.find_element_by_xpath(".//android.widget.LinearLayout[1]/android.widget.TextView[1]")
    print(text_div.text)





if __name__ == '__main__':
    '''
    17061789774
    16531165344
    16533431172
    16534167512
    16535511249
    16538804211
    16517865360
    16573052721
    16222617977
    17169479357
    16574980930
    '''
    driver = get_driver()
    signup_car168(driver)

