import base64
import datetime
import hashlib
import random
import re
import time
from common.yaml_handler import YamlHandler


class DebugTalk:
    """接口测试动态数据处理工具（加密、时间戳、关联变量提取等）"""

    def __init__(self):
        self.read = YamlHandler()

    def get_extract_data(self, node_name, randoms=None):
        """
        获取extract.yaml数据，首先判断randoms是否为数字类型，如果不是就获取下一个node节点的数据
        :param node_name: extract.yaml 中的 key
        :param randoms: 取值模式
            - None: 按原始 key 取值
            - 数字字符串:
                0  → 随机取一个值
                -1 → 全部拼接为逗号分隔字符串
                -2 → 全部拆分为列表
                其他正整数 → 按顺序取值（1 表示第一个）
            - 非数字字符串: 作为二级 key 取值
        """
        data = self.read.get_extract_yaml(node_name)
        # 判断 randoms 是否为数字
        if randoms is not None and re.match(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$', str(randoms)):
            randoms = int(randoms)
            # 按模式映射取值
            data_value = {
                randoms: self.get_extract_order_data(data, randoms),
                0: random.choice(data),
                -1: ','.join(data),
                -2: ','.join(data).split(','),
            }
            data = data_value[randoms]
        else:
            data = self.read.get_extract_yaml(node_name, randoms)
        return data

    def get_extract_order_data(self, data, randoms):
        """按顺序取数据，randoms 从 1 开始计数（1 = 第一个）"""
        if randoms not in (0, -1, -2):
            return data[randoms - 1]
        return None

    def md5_encryption(self, params):
        """参数 MD5 加密，返回十六进制字符串"""
        return hashlib.md5(params.encode('utf-8')).hexdigest()

    def base64_encryption(self, params):
        """参数 Base64 加密，返回编码后字节串"""
        return base64.b64encode(params.encode('utf-8'))

    def timestamp(self):
        """获取当前 10 位时间戳（秒级）"""
        return int(time.time())

    def timestamp_thirteen(self):
        """获取当前 13 位时间戳（毫秒级）"""
        return int(time.time() * 1000)

    def end_time(self):
        """获取当前时间，格式：YYYY-MM-DD HH:MM:SS"""
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def end_year_time(self):
        """获取当前日期，格式：YYYY-MM-DD"""
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def get_baseurl(self, host):
        """从配置文件读取 api_envi 段下的接口地址"""
        from config.operationConfig import OperationConfig
        return OperationConfig().get_section_for_data('api_envi', host)