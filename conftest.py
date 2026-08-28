# -*- coding: utf-8 -*-
import warnings
import pytest

from common.feishuRobot import send_feishu_msg
from common.yaml_handler import YamlHandler
from common.recordlog import logs
from base.removefile import remove_file
from common.dingRobot import send_dd_msg
from config.setting import DD_MSG, FS_MSG
# from config.setting import JENKINS_ENHANCE

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

# 钩子函数，测试结束后执行
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """测试结束后收集结果摘要，并按配置推送通知"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    # pytest 9.x 中 _session_start 是 Instant 对象，通过 elapsed().seconds 获取耗时（秒）
    duration = terminalreporter._session_start.elapsed().seconds

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

    # Jenkins 构建信息增强：追加构建编号与报告链接，方便收到通知后直接点击查看
    # 本地运行或 Jenkins 不可达时查询会失败，捕获后降级为普通通知，不影响测试流程
    # if JENKINS_ENHANCE:
    #     try:
    #         from common.jenkins_handler import JenkinsHandler
    #         build_info = JenkinsHandler().get_build_enhance_info()
    #         summary += (
    #             f"\n构建编号：第{build_info['build_number']}次"
    #             f"\n构建地址：{build_info['build_url']}"
    #             f"\nAllure 报告：{build_info['allure_url']}"
    #         )
    #     except Exception as e:
    #         logs.error(f'查询 Jenkins 构建信息失败，降级发送普通通知：{e}')

    if DD_MSG:
        send_dd_msg(summary)
    if FS_MSG:
        send_feishu_msg(summary)
