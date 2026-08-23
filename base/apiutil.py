import json
import re
import allure
import jsonpath

from json.decoder import JSONDecodeError
from common.assertions import Assertions
from common.debugtalk import DebugTalk
from common.yaml_handler import YamlHandler
from common.recordlog import logs
from common.sendrequest import SendRequest
from config.operationConfig import OperationConfig


class RequestBase:
    """接口请求基类，处理 yaml 数据解析、请求发送、结果提取与断言"""

    def __init__(self):
        self.run = SendRequest()
        self.conf = OperationConfig()
        self.read = YamlHandler()
        self.asserts = Assertions()

    def replace_load(self, data):
        """
        热加载
        解析 yaml 数据中的 ${func_name(params)} 占位符，
        通过反射调用 DebugTalk 中的方法完成动态替换
        """
        str_data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
        # 逐个替换 ${...} 占位符
        for _ in range(str_data.count('${')):
            if '${' not in str_data or '}' not in str_data:
                break
            start = str_data.index('$')
            end = str_data.index('}', start)
            ref_all = str_data[start:end + 1]
            # 解析函数名和参数
            func_name = ref_all[2:ref_all.index("(")]
            func_params = ref_all[ref_all.index("(") + 1:ref_all.index(")")]
            # 通过反射调用 DebugTalk 对应方法
            args = func_params.split(',') if func_params else ""
            result = getattr(DebugTalk(), func_name)(*args)
            # 列表结果拼接为字符串
            if result and isinstance(result, list):
                result = ','.join(result)
            str_data = str_data.replace(ref_all, str(result))
        # 原始数据为字典时还原为 dict
        return json.loads(str_data) if data and isinstance(data, dict) else str_data

    def specification_yaml(self, base_info, test_case):
        """
        接口请求处理主流程：解析参数 → 发送请求 → 提取数据 → 执行断言
        :param base_info: yaml 文件中的 baseInfo 段
        :param test_case: yaml 文件中的 testCase 段
        """
        params_type = ['data', 'json', 'params']
        # 解析接口基本信息
        url_host = self.conf.get_section_for_data('api_envi', 'host')
        api_name = base_info['api_name']
        url = url_host + base_info['url']
        method = base_info['method']
        header = self.replace_load(base_info['header'])
        # 记录请求信息到 allure 报告
        allure.attach(f'接口名称：{api_name}', api_name, allure.attachment_type.TEXT)
        allure.attach(f'接口地址：{url}', api_name, allure.attachment_type.TEXT)
        allure.attach(f'请求方法：{method}', api_name, allure.attachment_type.TEXT)
        allure.attach(f'请求头：{header}', api_name, allure.attachment_type.TEXT)
        # 处理 cookie（替换占位符后 eval 转为字典）
        cookie = None
        if base_info.get('cookies') is not None:
            cookie = eval(self.replace_load(base_info['cookies']))
        case_name = test_case.pop('case_name')
        allure.attach(f'测试用例名称：{case_name}', api_name, allure.attachment_type.TEXT)
        # 处理断言和参数提取配置
        validation = eval(self.replace_load(test_case.get('validation')))
        extract = test_case.pop('extract', None)
        extract_list = test_case.pop('extract_list', None)
        # 替换请求参数中的占位符
        for key, value in test_case.items():
            if key in params_type:
                test_case[key] = self.replace_load(value)

        # 处理文件上传
        files = None
        file = test_case.pop('files', None)
        if file is not None:
            for fk, fv in file.items():
                allure.attach(json.dumps(file), '导入文件')
                files = {fk: open(fv, mode='rb')}
        # 发送请求
        res = self.run.run_main(name=api_name, url=url, case_name=case_name,
                                header=header, method=method,
                                file=files, cookies=cookie, **test_case)
        status_code = res.status_code
        allure.attach(self.allure_attach_response(res.json()), '接口响应信息', allure.attachment_type.TEXT)
        # 解析响应、提取数据、执行断言
        try:
            res_json = json.loads(res.text)
            if extract is not None:
                self.extract_data(extract, res.text)
            if extract_list is not None:
                self.extract_data_list(extract_list, res.text)
            self.asserts.assert_result(validation, res_json, status_code)
        except JSONDecodeError:
            logs.error('系统异常或接口未请求！')
            raise
        except Exception as e:
            logs.error(f"断言或提取异常: {e}")
            raise

    @staticmethod
    def allure_attach_response(response):
        """格式化响应数据用于 allure 报告展示"""
        return json.dumps(response, ensure_ascii=False, indent=4) if isinstance(response, dict) else response

    def extract_data(self, testcase_extract, response):
        """
        提取接口返回值（单值），支持正则和 jsonpath 两种方式
        :param testcase_extract: yaml 中 extract 段的键值对
        :param response: 接口实际返回值（字符串）
        """
        regex_patterns = ['(.*?)', '(.+?)', r'(\d)', r'(\d*)']
        try:
            for key, value in testcase_extract.items():
                # 正则表达式提取
                for pat in regex_patterns:
                    if pat in value:
                        ext = re.search(value, response)
                        # 数字模式转为 int
                        extracted = int(ext.group(1)) if pat in [r'(\d+)', r'(\d*)'] else ext.group(1)
                        self.read.write_yaml_data({key: extracted})
                # jsonpath 提取
                if '$' in value:
                    result = jsonpath.search(value, json.loads(response))
                    if result:
                        logs.info(f'提取接口的返回值：{key}={result[0]}')
                        self.read.write_yaml_data({key: result[0]})
                    else:
                        self.read.write_yaml_data({key: '未提取到数据，请检查接口返回值是否为空！'})
        except Exception as e:
            logs.error(f"数据提取异常: {e}")

    def extract_data_list(self, testcase_extract_list, response):
        """
        提取接口返回值（多值列表），支持正则和 jsonpath 两种方式
        :param testcase_extract_list: yaml 中 extract_list 段的键值对
        :param response: 接口实际返回值（字符串）
        """
        try:
            for key, value in testcase_extract_list.items():
                # 正则提取（返回所有匹配项列表）
                if "(.+?)" in value or "(.*?)" in value:
                    ext_list = re.findall(value, response, re.S)
                    if ext_list:
                        logs.info(f'正则提取到的参数：{key}={ext_list}')
                        self.read.write_yaml_data({key: ext_list})
                # jsonpath 提取
                if "$" in value:
                    ext_json = jsonpath.search(value, json.loads(response))
                    extract_data = {key: ext_json} if ext_json else {key: "未提取到数据，该接口返回结果可能为空"}
                    logs.info(f'json提取到参数：{extract_data}')
                    self.read.write_yaml_data(extract_data)
        except Exception:
            logs.error('接口返回值提取异常，请检查yaml文件extract_list表达式是否正确！')