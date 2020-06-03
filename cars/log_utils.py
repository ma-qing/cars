# logging配置
import json
import logging
import os
import logging.config
from cars.settings import BASE_DIR

BASE_LOG_DIR = os.path.join(BASE_DIR, "log")
if not os.path.exists(BASE_LOG_DIR):
    os.mkdir(os.path.join(BASE_DIR, "log"))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(name)s:%(filename)s:%(lineno)d:%(levelname)s]-- %(message)s'
        },

    },
    'handlers': {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        'error': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据文件大小自动切
            'filename': os.path.join(BASE_LOG_DIR, "error.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 5,  # 备份数为3  xx.log --> xx.log.1 --> xx.log.2 --> xx.log.3
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'car168_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据时间自动切
            'filename': os.path.join(BASE_LOG_DIR, "car168_info.log"),  # 日志文件
            'backupCount': 10,  # 备份数为3  xx.log --> xx.log.2018-08-23_00-00-00 --> xx.log.2018-08-24_00-00-00 --> ...
            # 'when': 'D',  # 每天一切， 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'nnqc_info': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据时间自动切
                    'filename': os.path.join(BASE_LOG_DIR, "nnqc_info.log"),  # 日志文件
                    'backupCount': 10,  # 备份数为3  xx.log --> xx.log.2018-08-23_00-00-00 --> xx.log.2018-08-24_00-00-00 --> ...
                    # 'when': 'D',  # 每天一切， 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
                    'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
                    'formatter': 'standard',
                    'encoding': 'utf-8',
                },
        'chezhen_info': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据时间自动切
                    'filename': os.path.join(BASE_LOG_DIR, "chezhen_info.log"),  # 日志文件
                    'backupCount': 10,  # 备份数为3  xx.log --> xx.log.2018-08-23_00-00-00 --> xx.log.2018-08-24_00-00-00 --> ...
                    # 'when': 'D',  # 每天一切， 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
                    'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
                    'formatter': 'standard',
                    'encoding': 'utf-8',
                },

    },
    'loggers': {
        'error': {  # 默认的logger应用如下配置
            'handlers': ["console",'error'],  # 上线之后可以把'console'移除
            'level': 'DEBUG',
            'propagate': True,
        },
        'car168': {  # 默认的logger应用如下配置
            'handlers': ["console", 'car168_info'],  # 上线之后可以把'console'移除
            'level': 'DEBUG',
            'propagate': True,
        },
        'nnqc': {  # 默认的logger应用如下配置
                    'handlers': ["console", 'nnqc_info'],  # 上线之后可以把'console'移除
                    'level': 'DEBUG',
                    'propagate': True,
                },
        'chezhen': {  # 默认的logger应用如下配置
                    'handlers': ["console", 'chezhen_info'],  # 上线之后可以把'console'移除
                    'level': 'DEBUG',
                    'propagate': True,
                },

    },
}


class SelfLog():
    def __init__(self,loggername, logfile=None):

        self.logger = logging.getLogger(loggername)
        # with open("logconf.json","r") as config:
        # LOGGING_CONFIG = json.load(LOGGING)
        logging.config.dictConfig(LOGGING)
if __name__ == '__main__':
    log = SelfLog('error')
    log.logger.error("ahhh")

# import logging, logging.handlers
# import time
#
# '''
# TimedRotatingFileHandler构造函数声明
# class logging.handlers.TimedRotatingFileHandler(filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None)
# filename    日志文件名前缀
# when        日志名变更时间单位
#     'S' Seconds
#     'M' Minutes
#     'H' Hours
#     'D' Days
#     'W0'-'W6' Weekday (0=Monday)
#     'midnight' Roll over at midnight
# interval    间隔时间，是指等待N个when单位的时间后，自动重建文件
# backupCount 保留日志最大文件数，超过限制，删除最先创建的文件；默认值0，表示不限制。
# delay       延迟文件创建，直到第一次调用emit()方法创建日志文件
# atTime      在指定的时间（datetime.time格式）创建日志文件。
# '''
#
# def test_TimedRotatingFileHandler():
#     # 定义日志输出格式
#     fmt_str = '[%(asctime)s][%(name)s:%(filename)s:%(lineno)d] [%(processName)s:%(funcName)s:%(levelname)s]- %(message)s'
#
#     # 初始化
#     logging.basicConfig()
#
#     # 创建TimedRotatingFileHandler处理对象
#     # 间隔5(S)创建新的名称为myLog%Y%m%d_%H%M%S.log的文件，并一直占用myLog文件。
#     fileshandle = logging.handlers.TimedRotatingFileHandler('myLog', when='S', interval=5, backupCount=3)
#     # 设置日志文件后缀，以当前时间作为日志文件后缀名。
#     fileshandle.suffix = "%Y%m%d_%H%M%S.log"
#     # 设置日志输出级别和格式
#     fileshandle.setLevel(logging.DEBUG)
#     formatter = logging.Formatter(fmt_str)
#     fileshandle.setFormatter(formatter)
#     # 添加到日志处理对象集合
#     logging.getLogger('').addHandler(fileshandle)
#
# if __name__ == '__main__':
#     test_TimedRotatingFileHandler()
#
#     # 测试在200s内创建文件多个日志文件
#     for i in range(0, 100):
#         logging.debug("logging.debug")
#         logging.info("logging.info")
#         logging.warning("logging.warning")
#         logging.error("logging.error")
#
#
#         time.sleep(2)