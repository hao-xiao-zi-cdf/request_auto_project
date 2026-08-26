import re
import jenkins
from config.operationConfig import OperationConfig

class JenkinsHandler:
    """Jenkins 操作类，封装构建查询、状态获取、测试报告统计等功能"""

    def __init__(self):
        conf = OperationConfig()
        self.__server = jenkins.Jenkins(
            url=conf.get_section_jenkins('url'),
            username=conf.get_section_jenkins('username'),
            password=conf.get_section_jenkins('password'),
            timeout=int(conf.get_section_jenkins('timeout'))
        )
        self.job_name = conf.get_section_jenkins('job_name')

    def get_job_number(self):
        """读取当前 job 的最新构建号"""
        return self.__server.get_job_info(self.job_name)['lastBuild']['number']

    def get_build_job_status(self):
        """读取最新构建的状态"""
        build_num = self.get_job_number()
        return self.__server.get_build_info(self.job_name, build_num)['result']

    def get_console_log(self):
        """获取最新构建的控制台日志"""
        return self.__server.get_build_console_output(self.job_name, self.get_job_number())

    def get_job_description(self):
        """返回 job 描述信息和 URL（单次请求获取）"""
        job_info = self.__server.get_job_info(self.job_name)
        return job_info['description'], job_info['url']

    def get_build_report(self):
        """获取最新构建的测试报告"""
        return self.__server.get_build_test_report(self.job_name, self.get_job_number())

    def report_success_or_fail(self):
        """
        统计测试报告的成功数、失败数、跳过数、成功率及执行时长，
        并从控制台日志中提取 allure 报告链接
        :return: 包含统计信息和报告链接的字典
        """
        report_info = self.get_build_report()
        pass_count = report_info['passCount']
        fail_count = report_info['failCount']
        skip_count = report_info['skipCount']
        total_count = pass_count + fail_count + skip_count
        duration = int(report_info['duration'])

        # 将秒数转换为"X时X分X秒"格式
        hour, remainder = divmod(duration, 3600)
        minute, seconds = divmod(remainder, 60)
        execute_duration = f'{hour}时{minute}分{seconds}秒'

        # 从控制台日志中提取 allure 报告链接
        console_log = self.get_console_log()
        report_line = re.search(
            rf'http://[\d.]+:\d+/job/{self.job_name}/(.*?)allure', console_log
        ).group(0)

        return {
            'total': total_count,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'skip_count': skip_count,
            'execute_duration': execute_duration,
            'report_line': report_line
        }
