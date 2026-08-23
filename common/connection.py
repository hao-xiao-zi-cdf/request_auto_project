import pymysql
from config.operationConfig import OperationConfig
from common.recordlog import logs


class ConnectMysql:
    """MySQL 数据库连接与操作封装"""

    def __init__(self):
        conf = OperationConfig()
        self.mysql_conf = {
            'host': conf.get_section_mysql('host'),
            'port': int(conf.get_section_mysql('port')),
            'user': conf.get_section_mysql('username'),
            'password': conf.get_section_mysql('password'),
            'database': conf.get_section_mysql('database'),
        }
        try:
            # 创建数据库连接对象
            self.conn = pymysql.connect(**self.mysql_conf, charset='utf8')
            # 创建sql执行对象cursor，并使用 DictCursor，查询结果以字典形式返回（字段名: 值）
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info(f"成功连接 MySQL — host: {self.mysql_conf['host']}, "
                      f"port: {self.mysql_conf['port']}, db: {self.mysql_conf['database']}")
        except Exception as e:
            logs.error(f"连接 MySQL 失败: {e}")

    def close(self):
        """关闭游标和数据库连接"""
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()

    def query_all(self, sql):
        """
        执行查询 SQL，返回第一条记录的值列表
        :param sql: 查询语句
        :return: [[val1, val2, ...], [val1, val2, ...], ...]，无数据时返回 None
        """
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            res = self.cursor.fetchall()
            if res:
                return [list(row.values()) for row in res]
        except Exception as e:
            logs.error(f"查询异常: {e}")
        finally:
            self.close()

    def delete(self, sql):
        """
        执行删除 SQL
        :param sql: 删除语句
        """
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            logs.info('删除成功')
        except Exception as e:
            logs.error(f"删除异常: {e}")
        finally:
            self.close()
