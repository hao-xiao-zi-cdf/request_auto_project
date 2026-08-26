import logging
import os
import sys

"""
放置框架运行所需的基础参数——路径、日志级别、超时时间、报告类型、通知开关，不随环境变化
"""

# 基础路径
DIR_BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_BASE)

# log日志输出级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = logging.DEBUG  # 文件
STREAM_LOG_LEVEL = logging.DEBUG  # 控制台

# 接口超时时间，单位/s
API_TIMEOUT = 60

# 生成的测试报告类型，可以生成两个风格的报告，allure或tm
REPORT_TYPE = 'allure'
# REPORT_TYPE = 'tm'

# 是否发送钉钉消息
DD_MSG = True

# 是否发送飞书消息
FS_MSG = True

# 文件路径
FILE_PATH = {
    'CONFIG': os.path.join(DIR_BASE, 'config/config_test.yaml'),
    'LOG': os.path.join(DIR_BASE, 'logs'),
    'YAML': os.path.join(DIR_BASE),
    'TEMP': os.path.join(DIR_BASE, 'report/temp'), # Allure原始报告数据目录
    'TMR': os.path.join(DIR_BASE, 'report/tmreport'), # 离线报告文档
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
