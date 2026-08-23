import json
import allure
import pytest
import requests
import urllib3

from config import setting
from common.recordlog import logs
from common.yaml_handler import YamlHandler

# 全局禁用 SSL 不安全请求警告，避免重复调用
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SendRequest:
    """发送接口请求，支持 GET 和 POST 方法"""

    def __init__(self, cookie=None):
        self.cookie = cookie
        self.yamlHandler = YamlHandler()

    @staticmethod
    def _parse_response(response):
        """
        解析响应对象，提取状态码、文本、body 和响应时间
        :param response: requests.Response 对象
        :return: 包含响应信息的字典
        """
        return {
            'code': response.status_code, # 接口响应状态码
            'text': response.text, # 接口响应文本
            'body': response.json().get('body') if response.headers.get('content-type', '').startswith('application/json') else '',
            'res_ms': response.elapsed.microseconds / 1000, # 响应时间/毫秒
            'res_second': response.elapsed.total_seconds(), # 响应时间/秒
        }

    def get(self, url, data, header):
        """
        发送 GET 请求
        :param url: 接口地址
        :param data: 请求参数
        :param header: 请求头
        :return: 响应信息字典，请求失败返回 None
        """
        try:
            response = requests.get(url, params=data, headers=header,
                                    cookies=self.cookie, verify=False)
        except Exception as e:
            logs.error(f"GET 请求异常: {e}")
            return None
        return self._parse_response(response)

    def post(self, url, data, header):
        """
        发送 POST 请求
        :param url: 接口地址
        :param data: 请求参数
        :param header: 请求头
        :return: 响应信息字典，请求失败返回 None
        """
        try:
            response = requests.post(url, data=data, headers=header,
                                     cookies=self.cookie, verify=False)
        except Exception as e:
            logs.error(f"POST 请求异常: {e}")
            return None
        return self._parse_response(response)

    def send_request(self, **kwargs):
        """
        通过 session 发送请求，自动处理 cookie 持久化
        :param kwargs: 传递给 session.request 的参数
        :return: Response 对象
        """
        session = requests.session()
        result = None
        try:
            result = session.request(**kwargs)
            set_cookie = requests.utils.dict_from_cookiejar(result.cookies)
            if set_cookie:
                cookie = {'Cookie': set_cookie}
                self.yamlHandler.write_yaml_data(cookie)
                logs.info(f"cookie：{cookie}")
            logs.info(f"接口返回信息：{result.text if result.text else result}")
        except requests.exceptions.ConnectionError:
            logs.error("ConnectionError -- 连接异常")
            pytest.fail("接口请求异常，可能是 request 的连接数过多或请求速度过快导致程序报错！")
        except requests.exceptions.HTTPError:
            logs.error("HTTPError -- http 异常")
        except requests.exceptions.RequestException as e:
            logs.error(f"RequestException: {e}")
            pytest.fail("请求异常，请检查系统或数据是否正常！")
        return result

    def run_main(self, name, url, case_name, header, method,
                 cookies=None, file=None, **kwargs):
        """
        接口请求入口，记录日志并发送请求
        :param name: 接口名
        :param url: 接口地址
        :param case_name: 测试用例名称
        :param header: 请求头
        :param method: 请求方法
        :param cookies: 默认为空
        :param file: 上传文件
        :param kwargs: 请求参数
        :return: Response 对象
        """
        try:
            # 记录请求信息
            logs.info(f'接口名称：{name}')
            logs.info(f'请求地址：{url}')
            logs.info(f'请求方式：{method}')
            logs.info(f'测试用例名称：{case_name}')
            logs.info(f'请求头：{header}')
            logs.info(f'Cookie：{cookies}')
            # 记录请求参数并附加到 allure 报告
            req_params = json.dumps(kwargs, ensure_ascii=False)
            if kwargs.keys() & {'data', 'json', 'params'}:
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info(f"请求参数：{kwargs}")
        except Exception as e:
            logs.error(f"记录请求日志异常: {e}")

        response = self.send_request(method=method, url=url, headers=header,
                                     cookies=cookies, files=file,
                                     timeout=setting.API_TIMEOUT,
                                     verify=False, **kwargs)
        return response