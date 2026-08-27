import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config.operationConfig import OperationConfig
from common.recordlog import logs

conf = OperationConfig()

class SendEmail:
    """构建并发送邮件（支持正文、附件）"""

    def __init__(
            self,
            host=conf.get_section_for_data('EMAIL', 'host'),
            user=conf.get_section_for_data('EMAIL', 'user'),
            passwd=conf.get_section_for_data('EMAIL', 'passwd')):
        self.__host = host
        self.__user = user
        self.__passwd = passwd

    def build_content(self, subject, email_content, addressee=None, atta_file=None):
        """
        构建并发送邮件
        :param subject: 邮件主题
        :param email_content: 邮件正文内容
        :param addressee: 收件人，多个以分号分隔；为空时读取配置文件
        :param atta_file: 附件文件路径（可选）
        """
        sender = f'liaison officer<{self.__user}>'
        # 收件人：未指定时从配置文件读取
        if addressee is None:
            addressee = conf.get_section_for_data('EMAIL', 'addressee').split(';')
        else:
            addressee = addressee.split(';')

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender
        # 提取邮箱前缀作为收件人显示名
        message['To'] = ';'.join(
            f'{re.match(r"([^@]+)", addr).group(1)}<{addr}>' for addr in addressee
        )

        # 邮件正文
        message.attach(MIMEText(email_content, _subtype='plain', _charset='utf-8'))

        # 附件（使用 with 确保文件正确关闭）
        if atta_file is not None:
            with open(atta_file, 'rb') as f:
                atta = MIMEApplication(f.read())
            atta['Content-Type'] = 'application/octet-stream'
            atta['Content-Disposition'] = 'attachment; filename="testresult.xls"'
            message.attach(atta)

        try:
            service = smtplib.SMTP_SSL(self.__host)
            service.login(self.__user, self.__passwd)
            service.sendmail(sender, addressee, message.as_string())
            service.quit()
        except smtplib.SMTPConnectError as e:
            logs.error(f'邮箱服务器连接失败：{e}')
        except smtplib.SMTPAuthenticationError as e:
            logs.error(f'邮箱服务器认证错误（POP3/SMTP服务未开启或授权码错误）：{e}')
        except smtplib.SMTPSenderRefused as e:
            logs.error(f'发件人地址未经验证：{e}')
        except smtplib.SMTPDataError as e:
            logs.error(f'邮件内容被拒绝（可能包含未许可信息或被识别为垃圾邮件）：{e}')
        except Exception as e:
            logs.error(f'邮件发送出现未知错误：{e}')
        else:
            logs.info('邮件发送成功!')


class BuildEmail(SendEmail):
    """组装测试结果摘要并发送邮件"""

    def _compose_and_send(self, success_num, fail_num, error_num, notrun_num,
                          extra_info='', atta_file=None):
        """
        统计通过率、组装邮件正文并发送（两种统计入口的公共逻辑）
        :param success_num: 通过数量
        :param fail_num: 失败数量
        :param error_num: 错误数量
        :param notrun_num: 未执行数量
        :param extra_info: 正文末尾追加的补充信息（如执行时长、报告链接）
        :param atta_file: 附件路径（可选）
        """
        total = success_num + fail_num + error_num + notrun_num
        execute_case = success_num + fail_num

        # 防止除零错误
        if execute_case == 0:
            pass_result = fail_result = err_result = '0.00%'
        else:
            pass_result = f'{success_num / execute_case * 100:.2f}%'
            fail_result = f'{fail_num / execute_case * 100:.2f}%'
            err_result = f'{error_num / execute_case * 100:.2f}%'

        subject = conf.get_section_for_data('EMAIL', 'subject')
        addressee = conf.get_section_for_data('EMAIL', 'addressee')
        content = (
            f'     ***项目接口测试，共测试接口{total}个，'
            f'通过{success_num}个，失败{fail_num}个，'
            f'错误{error_num}个，未执行{notrun_num}个，'
            f'通过率{pass_result}，失败率{fail_result}，错误率{err_result}。'
            f'{extra_info}'
        )
        self.build_content(subject, content, addressee, atta_file)

    def main(self, success, failed, error, not_running, atta_file=None):
        """
        按用例列表统计测试结果并发送邮件
        :param success: 通过的用例列表
        :param failed: 失败的用例列表
        :param error: 错误的用例列表
        :param not_running: 未执行的用例列表
        :param atta_file: 附件路径（可选）
        """
        self._compose_and_send(
            len(success), len(failed), len(error), len(not_running),
            '详细测试结果请参见附件。', atta_file
        )

    def main_by_counts(self, pass_count, fail_count, skip_count, error_count=0, extra_info=''):
        """
        按结果数量统计发送邮件（本地 pytest 统计、Jenkins 构建统计均可使用）
        :param pass_count: 通过数量
        :param fail_count: 失败数量
        :param skip_count: 跳过/未执行数量
        :param error_count: 错误数量（无错误分类时默认 0）
        :param extra_info: 正文末尾追加的补充信息（如执行时长、报告链接）
        """
        self._compose_and_send(pass_count, fail_count, error_count, skip_count, extra_info)