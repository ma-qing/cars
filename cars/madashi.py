# coding:utf-8
import json
import os
import random
import re
import time
from multiprocessing import Process

import requests
from fake_useragent import UserAgent
from requests.utils import get_encoding_from_headers

from cars.login import signup, get_auth
from cars.settings import BASE_DIR
from cars.utils import set_redis

cookie_r = set_redis(2)
username = "maxfire"
password = "ma123456"
# 牛牛汽车注册id
projectid_nnqc = "17883"
cookies_nnqc = "cookies_nnqc"

name_list = ["裴玉", "陈英", "赵兵", "9442", "戴国强", "陶洪万", "朱洪纯", "徐亚玲", "徐宗玲", "刘海琪", "曾辉", "唐转兵", "黄飞", "光光", "谢林华", "梁远述",
             "王波香", "王洪超", "刘江", "黄光平", "赵磊", "杨春香", "卢军", "谭恢来", "徐福海", "陈群华", "敬小玲", "王柏杨", "刘崇溶", "袁微", "冯世军", "袁舒含",
             "李贵君", "袁绍斌", "李定其", "罗江山", "王广芳", "孔宪全", "曹兴富", "游伟", "宁有洁", "陈桂香", "王恒英", "吴文模", "叶元凤", "陈德民", "樊艳林",
             "赵斌", "罗宏", "胡支陶", "胡支炎", "张伟", "丛占国", "赵一航", "徐子程", "傅长远", "赵秀宇", "王海龙", "张涛", "姜雪娜", "冷忠仁", "曹松", "张云",
             "丁伟深", "殷梓", "吴锦", "董文欣", "缪杰", "何慧", "吴明", "黄仁鹤", "陈锵", "谢中", "刘勇", "蒋周宁", "陈忠", ]

send_sucess = "success"
send_agin = "您的短信已发送,请勿重复提交"
registered = ""

# 验证手机号是否注册url
check_phone_url = "http://www.niuniuqiche.com/v2/ajax/vc/{}/generate"

headers = {
        "User-Agent": UserAgent().random
    }


# 获取token
def get_token(username, password):
    url = "http://43.249.193.217:81/logon/username={username}&password={password}".format(username=username, password=password)
    result = requests.get(url)
    status = result.text[0]
    token = result.text.split("|")[1]
    status = int(status)
    if status:
        return token
    else:
        print("获取tokenerror", token)
        return None


# 获取余额
def get_balance(token):
    url = "http://43.249.193.217:81/money/token={token}".format(token=token)
    result = requests.get(url)
    status = result.text.split("|")[0]
    # 剩余余额
    balance = result.text.split("|")[1]
    # 开发者剩余余额
    developer_balance = result.text.split("|")[0]
    status = int(status)
    if status:
        return float(balance)
    else:
        print("获取余额error", balance)
        return None

def get_phonenum(projectid, token, operator="", Region="", card=None, phone="", loop=1, filter="", teu="", pie=""):
    '''
    :param projectid: 项目id
    :param token: 登录token
    :param operator: 1=移动 2=联通 3=电信 [可空]
    :param Region: 上海 系统会自动筛选上海的号码 地区需要用UTF8进行编码 %E4%B8%8A%E6%B5%B7 [可空]
    :param card: 1=虚拟运营商 2=实卡 [可空]
    :param phone: 你要指定获取的号码,不传入号码情况下,获取新号码. [可空]
    :param loop: 1排除已做过号码取号时不会再获取到，2不过滤已做号码可以取号时循环获取号码（号码循环做业务必须选择2）
    :param filter: (排除号段170,171,165)
    :param teu: (排除地区 上海 地区需要用UTF8进行编码 %E4%B8%8A%E6%B5%B7 )
    :param pie: 指定号段135,137,138)
    :return:
    '''
    url = "http://43.249.193.217:81/Getnumber/id={projectid}&operator=&Region=&card=&phone={phone}&loop={loop}&filte={filter}&teu=&pie=&token={token}".format(
        projectid=projectid,
        operator=operator,
        Region=Region,
        card=card,
        phone=phone,
        loop=loop,
        filter=filter,
        teu=teu,
        pie=pie,
        token=token,
    )
    result= requests.get(url).content.decode()
    status = result.split("|")[0]
    phonenum = result.split("|")[1]
    status = int(status)
    if status:
        return phonenum
    else:
        print("获取手机号url", url)
        print("获取手机号error", phonenum)
        return None


def get_code(projectid, phonenum, token, matchrule, username="maxfire", processname=None):
    '''
    :param projectid:
    :param phonenum:
    :param token:
    :param usernmae:注册时候的用户名
    :return:
    '''
    url = "http://43.249.193.217:81/Getsms/id={projectid}&phone={phonenum}&t={username}&token={token}".format(
        projectid=projectid,
        phonenum=phonenum,
        token=token,
        username=username,
    )
    while True:
        time.sleep(3)
        result = requests.get(url).content.decode()
        status = result.split("|")[0]
        msg = result.split("|")[1]
        status = int(status)
        print("进程:%s验证码接受中***"%processname, result)
        if status:
            search_result = re.search(matchrule, msg, re.I)
            code = search_result.group(1)
            break

    return code
def relase_phonenum(projectid, phone_num, token):
    url = "http://43.249.193.217:81/release/id={projectid}&phone={phone_num}&token={token}".format(projectid=projectid, phone_num=phone_num, token=token)
    result = requests.get(url).content.decode()
    print(result)


# 组装拿到手机号
def build_phonenum(projectid, loop=1, phone="", filter=""):
    token = get_token(username, password)
    if token:
        balance = get_balance(token)
        print("所剩余额", balance)
        if balance:
            phonenum = get_phonenum(projectid=projectid, token=token, loop=loop, phone=phone, filter=filter)
            if phonenum:
                return token, phonenum
            else:
                return token, None
    else:
        print("没有收到手机号")
        return None, None


# 发送短信验证码
def check_isignup(token, phonenum, request_code,authtoken, s, processname=None):
    data = {
        'mobile': phonenum,
        "type": 0,
    }
    # proxies = {
    #     'http': get_proxy()
    # }

    result = s.post(check_phone_url.format(request_code), data=data, headers=headers,)
    return_dicts = eval(result.text)
    if return_dicts.get('status') == 200:
        matchrule = "验证码是(\d+),"
        code = get_code(projectid_nnqc, phonenum=phonenum, token=token, matchrule=matchrule, processname=processname)
        if code:
            print("接收到的验证码为:", code)
            signupstatus, return_headers, siginupresult = signup(s=s, phonenum=phonenum, code=code, password="ma123456", realname=random.choice(name_list), authtoken=authtoken)
            if signupstatus == 200:
                cookie = return_headers.get('Set-Cookie').split(";")[0]
                print("注册的cookie", cookie)
                print("返回结果", siginupresult)
                return cookie
        else:
            print("接码平台未返回验证码")

    elif return_dicts.get("status") == 400:
        # 已经注册了，只需要登录
        if return_dicts.get('notice') == registered:
            # 执行登录流行
            print("该号码已经注册")
            pass
        elif return_dicts.get('notice') == send_agin:
            # 不能重复发送验证码
            print("已经发送过验证码, 不能重复发送")
            pass
        else:
            print("验证码发送接口未知错误")
            pass


def create_cookie_nnqc(processname):
    # 从网页上拿下来的两个认证, 第一个用于发验证码时候认证，第二个用于点击注册上传参数时候
    s, authentoken, request_code = get_auth()
    print("网页拿到的认证", authentoken, request_code)
    # 接码平台接口拿到的token，手机号
    token, phone_nume = build_phonenum(projectid_nnqc, loop=1)
    print("接码平台拿到的数据", phone_nume, token)
    nnsession = check_isignup(token, phone_nume, request_code, authentoken, s, processname)
    print(nnsession)
    dicts = {}
    lists = nnsession.split("=")
    dicts[lists[0]] = lists[1]
    print(dicts)
    mapping = {json.dumps(dicts):int(phone_nume)}
    # with open("./nnqcookies.txt", "a", encoding="utf8") as f:
    #     f.write(mapping)

    cookie_r.zadd(cookies_nnqc, mapping)


# 获取代理
def get_proxy():
    with open(os.path.join(BASE_DIR, "proxies.txt"), "r") as f:
        date = f.read().splitlines()
        proxy = random.choice(date)
        print("请求的代理为:", proxy)
        return proxy

if __name__ == '__main__':
    # # 从网页上拿下来的两个认证, 第一个用于发验证码时候认证，第二个用于点击注册上传参数时候
    # s, authentoken, request_code = get_auth()
    # print("网页拿到的认证", authentoken, request_code)
    # # 接码平台接口拿到的token，手机号
    # token, phone_nume = build_phonenum()
    # print(token, phone_nume)
    # print(check_isignup(token, phone_nume, request_code, s))
    # signupstatus, return_headers, siginupresult = signup(s=s, phonenum="17056393488", code="5054", password="ma123456",realname=random.choice(name_list), authtoken=authentoken)

    prcess1 = Process(target=create_cookie_nnqc, args=("进程1",))
    prcess2 = Process(target=create_cookie_nnqc, args=("进程2",))
    prcess3 = Process(target=create_cookie_nnqc, args=("进程3",))
    prcess1.start()
    print("进程1开启************")
    prcess2.start()
    print("进程2开启************")
    prcess3.start()
    print("进程3开启************")
    prcess1.join()
    prcess2.join()
    prcess3.join()
