import os
import yaml
import traceback
from common.recordlog import logs
from config.operationConfig import OperationConfig
from config.setting import FILE_PATH

def get_testcase_yaml(file):
    """
    读取测试用例 yaml 文件
    当只有一个用例组时，将 baseInfo 与每个 testCase 组合后返回
    当有多个用例组时，直接返回原始数据
    """
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        # 单个用例组：提取 baseInfo 与每个 testCase 配对
        if len(data) <= 1:
            yam_data = data[0]
            base_info = yam_data.get('baseInfo')
            return [[base_info, ts] for ts in yam_data.get('testCase')]
        # 多个用例组：直接返回
        return data
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
        追加写入 dict 数据到 extract.yaml（用于接口关联）
        :param value: 写入数据，必须为 dict
        """
        file_path = FILE_PATH['EXTRACT']
        # 目录不存在时自动创建
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                if isinstance(value, dict):
                    yaml.dump(value, f, allow_unicode=True, sort_keys=False)
                else:
                    logs.info('写入 [extract.yaml] 的数据必须为 dict 格式')
        except Exception:
            logs.error(traceback.format_exc())

    def clear_yaml_data(self):
        """清空 extract.yaml 文件数据"""
        with open(FILE_PATH['EXTRACT'], 'w') as f:
            f.truncate()

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