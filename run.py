import shutil
import pytest
import os
import webbrowser
from config.setting import REPORT_TYPE, FILE_PATH

if __name__ == '__main__':
    # 报告输出目录
    report_temp = FILE_PATH['TEMP']
    report_tm = FILE_PATH['TMR']

    if REPORT_TYPE == 'allure':
        # 运行测试，生成allure原始数据和junit结果
        pytest.main([
            '-s', '-v',
            f'--alluredir={report_temp}',
            './testcase',
            '--clean-alluredir',
            f'--junitxml={FILE_PATH["RESULTXML"]}/results.xml'
        ])
        # 复制环境信息文件到allure数据目录
        shutil.copy('./environment.xml', report_temp)
        # 启动allure报告服务
        os.system(f'allure serve {report_temp}')

    elif REPORT_TYPE == 'tm':
        # 运行测试，生成tm风格HTML报告
        pytest.main([
            '-vs',
            '--pytest-tmreport-name=testReport.html',
            f'--pytest-tmreport-path={report_tm}'
        ])
        # 自动打开测试报告
        webbrowser.open_new_tab(f'{report_tm}/testReport.html')