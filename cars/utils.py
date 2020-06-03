import re

import redis
from pymysql import connect

from cars.items import CarStyleItem

MYDB = "cars"
HOST = "localhost"
USER = "root"
PASSWD = "ma123456"
charset="utf8mb4"
class Mysqlpython:
    def __init__(self,database=MYDB,host=HOST,user=USER,
                 password=PASSWD,port=3306,charset=charset):
        self.host=host
        self.user=user
        self.password=password
        self.port=port
        self.database=database
        self.charset=charset

# 数据库连接方法:
    def open(self):
        self.db=connect(host=self.host,user=self.user,
                        password=self.password,port=self.port,
                        database=self.database,
                        charset=self.charset)
#游标对象
        self.cur=self.db.cursor()
#数据库关闭方法:
    def close(self):
        self.cur.close()
        self.db.close()
#数据库执行操作方法:
    def execute(self,sql,L=[]):
        try:
            self.open()
            self.cur.execute(sql,L)
            self.db.commit()
            print("ok")
        except Exception as e:
            self.db.rollback()
            print("Failed", e)
            self.close()
            return False
        self.close()
        return True

# 数据库查询所有操作方法:
    def readall(self,sql,L=[]):
        try:
            self.open()
            self.cur.execute(sql,L)
            result=self.cur.fetchall()
            return result
        except Exception as e:
            print("Failed",e)
        self.close()


def set_redis(db=0):
    host = '127.0.0.1'
    port = 6379

    pool = redis.ConnectionPool(host=host, port=port, db=db)

    r = redis.StrictRedis(connection_pool=pool)
    return r


# 处理车型(去掉空格等其他因素)
def deal_style(car_style):
    car_style = " ".join(car_style.split())
    return car_style

# 年款匹配
def deal_year(car_style, obj):
    # 年款
    search_year = re.search('\d+款', car_style)
    if search_year:
        year = search_year.group()
    else:
        year = None
        obj.logger.info("车型{car_style}未匹配到年款信息".format(car_style=car_style))

    return year


# 处理排量信息
def deal_displacement(car_style, obj):
    search_displacement = re.search("\d+\.\d+Li|\d+Li|\d+\.\d+Le|\d+Le|\d+\.\d+T|\d+T|\d+\.\d+L|\d+L", car_style)
    if search_displacement:
        displacement = search_displacement.group()
    else:
        obj.logger.info("车型:{car_style}未匹配到排量信息".format(car_style=car_style))
        displacement = None
    return displacement


# 处理指导价格
def deal_guideprice(guide_price):
    # 匹配后的价格 XX.XX万
    select_guide_price = re.search("\d+\.\d+万|\d+万", guide_price, re.I)
    if select_guide_price:
        guide_price = select_guide_price.group()
    return guide_price


#保存item对象
def sav_item(brand, cartype, year, carstyle, guide_price, displacement, config, version_num, price, volume, platform, requesturl, rediskey, updatetime):
    carstyleitem = CarStyleItem()
    carstyleitem['brand'] = brand
    carstyleitem["type"] = cartype
    carstyleitem['year'] = year
    carstyleitem['style'] = carstyle
    carstyleitem['guide_price'] = str(guide_price)
    carstyleitem['displacement'] = displacement
    carstyleitem['configuration'] = str(config)
    carstyleitem['version'] = str(version_num)
    carstyleitem['status'] = "None"
    carstyleitem['price'] = price
    carstyleitem['volume'] = volume
    carstyleitem['platform'] = platform
    carstyleitem['detail_url'] = requesturl
    carstyleitem['rediskey'] = rediskey
    carstyleitem['updatetime'] = updatetime

    return carstyleitem


import smtplib
from email.header import Header
from email.mime.text import MIMEText

# 第三方 SMTP 服务
mail_host = "smtp.163.com"  # SMTP服务器
mail_user = "maxma66@163.com"  # 用户名
mail_pass = "REZGCQDYFWYPNYSU"  # 授权密码，非登录密码

sender = "maxma66@163.com"
receivers = ["maxma666@qq.com",]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

# content = 'cookie预警'
title = 'Cookie 出错'  # 邮件主题


def sendEmail(content):
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)


# def send_email2(SMTP_host, from_account, from_passwd, to_account, subject, content):
#     email_client = smtplib.SMTP(SMTP_host)
#     email_client.login(from_account, from_passwd)
#     # create msg
#     msg = MIMEText(content, 'plain', 'utf-8')
#     msg['Subject'] = Header(subject, 'utf-8')  # subject
#     msg['From'] = from_account
#     msg['To'] = to_account
#     email_client.sendmail(from_account, to_account, msg.as_string())
#
#     email_client.quit()

