import pytest
import allure
import os
import platform
import sys
from common.recordlog import logs
from base.apiutil import RequestBase
from config.setting import FILE_PATH
from config.operationConfig import OperationConfig
from common.yaml_handler import get_testcase_yaml
from common.connection import ConnectMysql

"""
-function：每一个函数或方法都会调用,默认为function
-class：每一个类调用一次，一个类中可以有多个方法
-module：每一个.py文件调用一次，该文件内又有多个function和class
-session：是多个文件调用一次，可以跨.py文件调用，每个.py文件就是module,整个会话只会运行一次
-autouse：默认为false，不会自动执行，需要手动调用，为true可以自动执行，不需要调用
"""

config = OperationConfig()

@pytest.fixture(autouse=True)
def start_test_and_end():
    logs.info('-------------接口测试开始--------------')
    yield
    logs.info('-------------接口测试结束--------------')

@pytest.fixture(scope='session', autouse=True)
def allure_environment():
    """
    动态写入 allure 报告的环境信息（environment.properties）
    """
    env_info = {
        'Python': sys.version.split()[0],
        'OS': f'{platform.system()} {platform.release()}',
        'BaseUrl': config.get_section_for_data('api_envi', 'host'),
        'environment': config.get_section_for_data('environment', 'type'),
        'Project': config.get_section_for_data('environment', 'project')
    }
    properties_path = os.path.join(FILE_PATH['TEMP'], 'environment.properties')
    os.makedirs(os.path.dirname(properties_path), exist_ok=True)
    with open(properties_path, 'w', encoding='ascii') as f:
        for key, value in env_info.items():
            # Java 的 properties 文件默认按 ISO-8859-1 解析，
            # 中文需转义为 \uXXXX 形式，否则 allure 报告中会显示乱码
            value = str(value).encode('unicode_escape').decode('ascii')
            f.write(f'{key}={value}\n')
    yield

@pytest.fixture(scope='session', autouse=True)
@allure.story("登录")
def system_login():
    try:
        api_info = get_testcase_yaml('./testdata/LoginManager/login_name.yaml')
        RequestBase().specification_yaml(api_info[0][0], api_info[0][1])
    except Exception as e:
        logs.error(f'登录接口出现异常，导致后续接口无法继续运行，请检查程序！，{e}')
        exit()

# @pytest.fixture(scope='session', autouse=True)
# def datadb_init():
#     """
#     数据库初始化与清理
#     测试前建立数据库连接（可预置测试数据），测试完成后清理测试数据并关闭连接，
#     避免产生脏数据影响系统
#     """
#     db = ConnectMysql()
#     logs.info('数据库连接已建立，准备开始测试')
#
#     # 如需预置测试数据，可在此处执行 INSERT SQL
#     # db.cursor.execute("INSERT INTO ...")
#     # db.conn.commit()
#
#     yield db
#
#     # 测试结束后清理测试数据
#     # db.delete("DELETE FROM ...")
#     db.close()
#     logs.info('测试数据已清理，数据库连接已关闭')
