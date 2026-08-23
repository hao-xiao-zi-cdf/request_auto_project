import os
from common.recordlog import logs

def remove_file(filepath, endlst):
    """
    删除指定目录下特定后缀的文件
    :param filepath: 目录路径
    :param endlst: 要删除的后缀列表，例如：['json', 'txt', 'attach']
    """
    try:
        if not isinstance(endlst, list):
            raise TypeError('endlst must be a list')

        if os.path.exists(filepath):
            for file_name in os.listdir(filepath):
                if any(file_name.endswith(ft) for ft in endlst):
                    os.remove(os.path.join(filepath, file_name))
        else:
            os.makedirs(filepath)
    except Exception as e:
        logs.error(e)


def remove_directory(path):
    """
    删除文件（注意：仅支持删除文件，不支持删除目录）
    :param path: 文件路径
    """
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logs.error(e)