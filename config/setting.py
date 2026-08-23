import logging
import os
import sys

DIR_BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_BASE)

# log日志输出级别
LOG_LEVEL = logging.DEBUG  # 文件
STREAM_LOG_LEVEL = logging.DEBUG  # 控制台

# 接口超时时间，单位/s
API_TIMEOUT = 60

# 生成的测试报告类型，可以生成两个风格的报告，allure或tm
REPORT_TYPE = 'allure'

# 是否发送钉钉消息
dd_msg = False

# 文件路径
FILE_PATH = {
    'CONFIG': os.path.join(DIR_BASE, 'config/config_test.yaml'),
    'LOG': os.path.join(DIR_BASE, 'logs'),
    'YAML': os.path.join(DIR_BASE),
    'TEMP': os.path.join(DIR_BASE, 'report/temp'),
    'TMR': os.path.join(DIR_BASE, 'report/tmreport'),
    'EXTRACT': os.path.join(DIR_BASE, 'extract.yaml'),
    'RESULTXML': os.path.join(DIR_BASE, 'report'),
}

# 默认请求头信息
LOGIN_HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}
