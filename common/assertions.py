import allure
import jsonpath
import operator

from common.recordlog import logs
from common.connection import ConnectMysql

class Assertions:
    """
    接口断言模块，支持以下断言模式：
    1) 响应文本字符串包含断言
    2) 响应结果相等 / 不相等断言
    3) 响应结果任意值断言
    4) 响应时间断言
    5) 数据库断言
    """

    def contains_assert(self, value, response, status_code):
        """
        字符串包含断言：断言预期结果的字符串是否包含在接口响应中
        :param value: 预期结果，yaml 文件中的断言配置
        :param response: 接口实际响应
        :param status_code: 响应状态码
        :return: 0 表示通过，非 0 表示失败
        """
        flag = 0
        for assert_key, assert_value in value.items():
            if assert_key == "status_code":
                # 状态码断言
                if assert_value != status_code:
                    flag += 1
                    allure.attach(f"预期结果：{assert_value}\n实际结果：{status_code}",
                                  '响应代码断言结果:失败', attachment_type=allure.attachment_type.TEXT)
                    logs.error(f"contains 断言失败：接口返回码【{status_code}】不等于【{assert_value}】")
            else:
                # 通过 jsonpath 提取响应中的字段值（注意：参数顺序为表达式在前，数据在后）
                resp_list = jsonpath.search(f"$..{assert_key}", response)
                if isinstance(resp_list[0], str):
                    resp_list = ''.join(resp_list)
                if resp_list:
                    # 预期值为 "NONE" 时视为 None
                    assert_value = None if assert_value.upper() == 'NONE' else assert_value
                    if assert_value in resp_list:
                        logs.info(f"字符串包含断言成功：预期结果【{assert_value}】,实际结果【{resp_list}】")
                    else:
                        flag += 1
                        allure.attach(f"预期结果：{assert_value}\n实际结果：{resp_list}",
                                      '响应文本断言结果：失败', attachment_type=allure.attachment_type.TEXT)
                        logs.error(f"响应文本断言失败：预期结果为【{assert_value}】,实际结果为【{resp_list}】")
        return flag

    def _compare_dict_assert(self, expected, actual, op_func, op_name):
        """
        字典比较断言（内部方法），提取相等/不相等断言的公共逻辑
        :param expected: 预期结果字典
        :param actual: 实际结果字典
        :param op_func: 比较函数（operator.eq 或 operator.ne）
        :param op_name: 操作名称（"相等" 或 "不相等"）
        :return: 0 表示通过，非 0 表示失败
        """
        if not (isinstance(expected, dict) and isinstance(actual, dict)):
            raise TypeError(f'{op_name}断言 -- 预期结果和实际响应结果必须为字典类型！')
        # 取第一个共同 key，构造实际结果子集进行比较
        common_key = list(expected.keys() & actual.keys())[0]
        new_actual = {common_key: actual[common_key]}
        result = op_func(new_actual, expected)
        if result:
            logs.info(f"{op_name}断言成功：实际结果：{new_actual}，预期结果：{expected}")
            allure.attach(f"预期结果：{expected}\n实际结果：{new_actual}",
                          f'{op_name}断言结果：成功', attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach(f"预期结果：{expected}\n实际结果：{new_actual}",
                          f'{op_name}断言结果：失败', attachment_type=allure.attachment_type.TEXT)
            logs.error(f"{op_name}断言失败：实际结果{new_actual}，预期结果：{expected}")
            return 1
        return 0

    def equal_assert(self, expected_results, actual_results):
        """相等断言"""
        return self._compare_dict_assert(expected_results, actual_results, operator.eq, "相等")

    def not_equal_assert(self, expected_results, actual_results):
        """不相等断言"""
        return self._compare_dict_assert(actual_results, expected_results, operator.ne, "不相等")

    def assert_response_any(self, actual_results, expected_results):
        """
        断言响应 body 中任意字段值是否匹配
        :param actual_results: 接口实际响应
        :param expected_results: 预期结果（单键值对）
        :return: 0 表示通过，非 0 表示失败
        """
        try:
            exp_key = list(expected_results.keys())[0]
            exp_value = list(expected_results.values())[0]
            if exp_key in actual_results and actual_results[exp_key] == exp_value:
                logs.info("响应结果任意值断言成功")
                return 0
            else:
                logs.error(f"响应结果任意值断言失败：预期 {exp_key}={exp_value}")
                return 1
        except Exception as e:
            logs.error(f"响应结果任意值断言异常: {e}")
            raise

    def assert_response_time(self, res_time, exp_time):
        """
        断言接口响应时间是否小于预期时间
        :param res_time: 实际响应时间（秒）
        :param exp_time: 预期响应时间（秒）
        """
        try:
            assert res_time < exp_time
            return True
        except AssertionError:
            logs.error(f'接口响应时间[{res_time}s]大于预期时间[{exp_time}s]')
            raise

    def assert_mysql_data(self, expected_results):
        """
        数据库断言：执行 SQL 查询，有数据则通过
        :param expected_results: SQL 语句
        :return: 0 表示通过，非 0 表示失败
        """
        conn = ConnectMysql()
        db_value = conn.query_all(expected_results)
        if db_value is not None:
            logs.info("数据库断言成功")
            return 0
        else:
            logs.error("数据库断言失败，请检查数据库是否存在该数据！")
            return 1

    # 断言类型 → 处理方法的映射
    ASSERT_DISPATCH = {
        'contains': 'contains_assert',
        'eq': 'equal_assert',
        'ne': 'not_equal_assert',
        'rv': 'assert_response_any',
        'db': 'assert_mysql_data',
    }

    def assert_result(self, expected, response, status_code):
        """
        断言总入口，根据 yaml 中的断言类型分发到对应的断言方法
        :param expected: 预期结果（包含断言类型和断言值的列表）
        :param response: 实际响应结果
        :param status_code: 响应状态码
        """
        all_flag = 0
        try:
            logs.info(f"yaml 文件预期结果：{expected}")
            for yq in expected:
                for key, value in yq.items():
                    method_name = self.ASSERT_DISPATCH.get(key)
                    if method_name is None:
                        logs.error(f"不支持的断言方式: {key}")
                        continue
                    method = getattr(self, method_name)
                    # contains 需要额外传 response 和 status_code
                    if key == 'contains':
                        all_flag += method(value, response, status_code)
                    elif key in ('eq', 'ne'):
                        all_flag += method(value, response)
                    else:
                        all_flag += method(response, value)
        except Exception:
            logs.error('接口断言异常，请检查 yaml 预期结果值是否正确填写!')
            raise

        assert all_flag == 0, "测试失败"