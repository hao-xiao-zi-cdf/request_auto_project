# -*- coding: utf-8 -*-
import time
import warnings
import pytest

from common.yaml_handler import YamlHandler
from base.removefile import remove_file
from common.dingRobot import send_dd_msg
from config.setting import DD_MSG

@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    """
    会话级初始化：
    1. 禁用 HTTPS ResourceWarning 告警
    2. 清空 extract.yaml（接口关联数据）
    3. 清理 allure 临时报告文件
    """
    warnings.simplefilter('ignore', ResourceWarning)
    YamlHandler().clear_yaml_data()
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """测试结束后收集结果摘要，并按配置推送钉钉通知"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    duration = time.time() - terminalreporter._sessionstarttime

    summary = (
        f"自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：\n"
        f"测试用例总数：{total}\n"
        f"测试通过数：{passed}\n"
        f"测试失败数：{failed}\n"
        f"错误数量：{error}\n"
        f"跳过执行数量：{skipped}\n"
        f"执行总时长：{duration}"
    )
    print(summary)

    if DD_MSG:
        send_dd_msg(summary)