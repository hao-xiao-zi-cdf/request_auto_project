import traceback
import configparser
from config import setting
# from common.recordlog import logs


class OperationConfig:
    """封装读取 *.ini 配置文件的工具类"""

    def __init__(self, filepath=None):
        # 未传入路径时使用默认配置路径
        self.__filepath = filepath or setting.FILE_PATH['CONFIG']

        self.conf = configparser.ConfigParser()
        try:
            self.conf.read(self.__filepath, encoding='utf-8')
        except Exception as e:
            print(f"读取配置文件失败: {e}")

        self.type = self.get_report_type('type')

    def get_item_value(self, section_name):
        """
        :param section_name: 根据ini文件的头部值获取全部值
        :return:以字典形式返回
        """
        return dict(self.conf.items(section_name))

    def get_section_for_data(self, section, option):
        """
        根据 section 和 option 获取对应的配置值
        :param section: ini 文件段名
        :param option: 段下的选项名
        :return: 配置值字符串，读取失败时返回空字符串
        """
        try:
            return self.conf.get(section, option)
        except Exception as e:
            print(f"读取配置项 [{section}] -> [{option}] 失败: {e}")
            return ''

    def write_config_data(self, section, option_key, option_value):
        """
        向 ini 配置文件中写入数据（仅当 section 不存在时写入）
        :param section: 段名
        :param option_key: 选项值 key
        :param option_value: 选项值 value
        """
        if section not in self.conf.sections():
            # 添加一个section值
            self.conf.add_section(section)
            self.conf.set(section, option_key, option_value)
            with open(self.__filepath, 'w', encoding='utf-8') as f:
                self.conf.write(f)
        else:
            print(f'"{section}" 已存在，写入失败')

    def get_section_mysql(self, option):
        """获取 MYSQL 段下的配置项"""
        return self.get_section_for_data("MYSQL", option)

    def get_report_type(self, option):
        """获取 REPORT_TYPE 段下的配置项"""
        return self.get_section_for_data('REPORT_TYPE', option)