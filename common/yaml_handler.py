import os
import yaml
import traceback
from common.recordlog import logs
from config.operationConfig import OperationConfig
from config.setting import FILE_PATH

def get_testcase_yaml(file):
    """
    读取测试用例 yaml 文件，将 baseInfo 与每条 testCase 组合
    :param file: yaml 测试用例文件路径
    :return: [[baseInfo1, testCase1], [baseInfo1, testCase2],[baseInfo2, testCase1]...] 格式的列表
             读取失败时返回 None
    """
    testcase_list = []
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            for item in data:
                base_info = item.get('baseInfo')
                for ts in item.get('testCase'):
                    testcase_list.append([base_info, ts])
            return testcase_list
    except UnicodeDecodeError:
        logs.error(f"[{file}] 文件编码格式错误，请确保 yaml 文件为 UTF-8 格式")
    except FileNotFoundError:
        logs.error(f'[{file}] 文件未找到，请检查路径是否正确')
    except Exception as e:
        logs.error(f'获取【{file}】文件数据时出现未知错误: {e}')


class YamlHandler:
    """读写接口的 YAML 格式测试数据"""

    def __init__(self, yaml_file=None):
        self.yaml_file = yaml_file
        self.conf = OperationConfig()
        self.yaml_data = None

    @property
    def get_yaml_data(self):
        """读取测试用例 yaml 数据，返回 list"""
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                self.yaml_data = yaml.safe_load(f)
                return self.yaml_data
        except Exception:
            logs.error(traceback.format_exc())

    def write_yaml_data(self, value):
        """
        写入 dict 数据到 extract.yaml（用于接口关联）
        采用"读旧数据→合并→整体写回"方式，同名 key 新值覆盖旧值，避免文件中出现重复 key
        :param value: 写入数据，必须为 dict
        """
        file_path = FILE_PATH['EXTRACT']
        # 目录不存在时自动创建
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not isinstance(value, dict):
            logs.info('写入 [extract.yaml] 的数据必须为 dict 格式')
            return
        try:
            # 读取已有数据并与新数据合并（新值覆盖旧值）
            ext_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as rf:
                    ext_data = yaml.safe_load(rf) or {}
            ext_data.update(value)
            # 整体写回，保证 key 不重复
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(ext_data, f, allow_unicode=True, sort_keys=False)
        except Exception:
            logs.error(traceback.format_exc())

    def clear_yaml_data(self):
        """清空 extract.yaml 文件数据"""
        with open(FILE_PATH['EXTRACT'], 'w') as f:
            f.truncate() # 是清空文件内容

    def get_extract_yaml(self, node_name, second_node_name=None):
        """
        读取 extract.yaml 中提取的变量值
        :param node_name: 一级 key
        :param second_node_name: 二级 key（可选）
        """
        # 文件不存在时自动创建
        if not os.path.exists(FILE_PATH['EXTRACT']):
            logs.error('extract.yaml 不存在')
            open(FILE_PATH['EXTRACT'], 'w').close()
            logs.info('extract.yaml 创建成功！')
        try:
            with open(FILE_PATH['EXTRACT'], 'r', encoding='utf-8') as rf:
                ext_data = yaml.safe_load(rf)
                if second_node_name is None:
                    return ext_data[node_name]
                return ext_data[node_name][second_node_name]
        except Exception as e:
            logs.error(f"【extract.yaml】没有找到：{node_name} -- {e}")