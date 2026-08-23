import pytest
import allure
from common.yaml_handler import get_testcase_yaml
from base.apiutil import RequestBase
from common.recordlog import logs
from common.connection import ConnectMysql

"""
-function：每一个函数或方法都会调用,默认为function
-class：每一个类调用一次，一个类中可以有多个方法
-module：每一个.py文件调用一次，该文件内又有多个function和class
-session：是多个文件调用一次，可以跨.py文件调用，每个.py文件就是module,整个会话只会运行一次
-autouse：默认为false，不会自动执行，需要手动调用，为true可以自动执行，不需要调用
"""


@pytest.fixture(autouse=True)
def start_test_and_end():
    logs.info('-------------接口测试开始--------------')
    yield
    logs.info('-------------接口测试结束--------------')


@pytest.fixture(scope='session', autouse=True)
@allure.story("登录")
def system_login():
    try:
        api_info = get_testcase_yaml('./data/loginName.yaml')
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
