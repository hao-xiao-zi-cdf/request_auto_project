import base64
import calendar
import datetime
import hashlib
import random
import re
import time
from common.yaml_handler import YamlHandler
from config.operationConfig import OperationConfig

# 一天的时间增量，用于日期偏移计算
Day = datetime.timedelta(days=1)

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

    # ==================== 加密方法 ====================

    def md5_encryption(self, params):
        """参数MD5加密"""
        return hashlib.md5(params.encode('utf-8')).hexdigest()

    def sha1_encryption(self, params):
        """参数SHA1加密"""
        return hashlib.sha1(params.encode('utf-8')).hexdigest()

    def base64_encryption(self, params):
        """Base64编码"""
        return base64.b64encode(params.encode('utf-8'))

    # ==================== 时间戳方法 ====================

    def timestamp(self):
        """获取当前时间戳，10位（秒级）"""
        return int(time.time())

    def timestamp_thirteen(self):
        """获取当前时间戳，13位（毫秒级）"""
        return int(time.time() * 1000)

    def today_zero_tenstamp(self):
        """获取当天00:00:00时间戳，10位"""
        return int(time.mktime(datetime.date.today().timetuple()))

    def today_zero_stamp(self):
        """获取当天00:00:00时间戳，13位"""
        return self.today_zero_tenstamp() * 1000

    def today_end_stamp(self):
        """获取当天23:59:59时间戳，13位"""
        tomorrow = datetime.date.today() + Day
        return (int(time.mktime(tomorrow.timetuple())) - 1) * 1000

    def specified_zero_tamp(self, days):
        """获取指定偏移日期的00:00:00时间戳，13位（days: 负数往前，正数往后）"""
        target_date = datetime.date.today() + datetime.timedelta(days=int(days))
        return int(time.mktime(target_date.timetuple())) * 1000

    def specified_end_tamp(self, days):
        """获取指定偏移日期的23:59:59时间戳，13位（days: 负数往前，正数往后）"""
        # 目标日期的下一天00:00:00减1秒即为当天23:59:59
        next_date = datetime.date.today() + datetime.timedelta(days=int(days) + 1)
        return (int(time.mktime(next_date.timetuple())) - 1) * 1000

    def month_first_time(self):
        """本月1号00:00:00时间戳，13位"""
        now = datetime.datetime.now()
        month_start = datetime.datetime(now.year, now.month, 1)
        return int(time.mktime(month_start.timetuple())) * 1000

    # ==================== 日期字符串方法 ====================

    def start_time(self):
        """获取当前时间的前一天，格式: YYYY-MM-DD HH:MM:SS"""
        return (datetime.datetime.now() - Day).strftime('%Y-%m-%d %H:%M:%S')

    def end_time(self):
        """获取当前时间，格式: YYYY-MM-DD HH:MM:SS"""
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def start_forward_time(self):
        """获取当前时间的前15天，格式: YYYY-MM-DD"""
        return (datetime.datetime.now() - 15 * Day).strftime('%Y-%m-%d')

    def start_after_time(self):
        """获取当前时间的后7天，格式: YYYY-MM-DD"""
        return (datetime.datetime.now() + 7 * Day).strftime('%Y-%m-%d')

    def end_year_time(self):
        """获取当前日期，格式: YYYY-MM-DD"""
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def month_start_time(self):
        """获取本月第一天，格式: YYYY-MM-DD"""
        now = datetime.datetime.now()
        return datetime.datetime(now.year, now.month, 1).strftime('%Y-%m-%d')

    def month_end_time(self):
        """获取本月最后一天，格式: YYYY-MM-DD"""
        now = datetime.datetime.now()
        last_day = calendar.monthrange(now.year, now.month)[1]
        return datetime.datetime(now.year, now.month, last_day).strftime('%Y-%m-%d')

    # ==================== 业务随机取值方法 ====================

    @staticmethod
    def _random_alarm(choices):
        """从候选列表中随机选取一个值"""
        return random.choice(choices)

    def fenceAlarm_alarmType_random(self):
        """围栏报警类型随机取值"""
        return self._random_alarm(["1", "3", "8", "2", "5", "6"])

    def fatigueAlarm_alarmType_random(self):
        """疲劳报警类型随机取值"""
        return self._random_alarm(["1", "3", "8"])

    def jurisdictionAlarm_random(self):
        """区域报警类型随机取值"""
        return self._random_alarm(["1", "3", "8", "2", "5", "6", "9"])

    # ==================== 配置读取方法 ====================

    def get_baseurl(self, host):
        """根据 host 键名从 api_envi 配置段读取对应的接口地址"""
        conf = OperationConfig()
        return conf.get_section_for_data('api_envi', host)