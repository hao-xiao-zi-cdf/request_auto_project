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
            './testcases',
            '--clean-alluredir',
            f'--junitxml={FILE_PATH["RESULTXML"]}/results.xml' #供Jenkins工具解析
        ])
        # 启动allure报告服务（chcp 65001 切换 UTF-8，避免 Ctrl+C 时 cmd 的中文退出提示乱码）
        os.system(f'chcp 65001 && allure serve {report_temp}')

    elif REPORT_TYPE == 'tm':
        # 运行测试，生成tm风格HTML报告
        pytest.main([
            '-vs',
            '--pytest-tmreport-name=testReport.html',
            f'--pytest-tmreport-path={report_tm}'
        ])
        # 浏览器自动打开测试报告
        webbrowser.open_new_tab(f'{report_tm}/testReport.html')