import allure
import pytest

from common.yaml_handler import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + '电子商务管理系统（业务场景）')
class TestEBusinessScenario:

    @allure.story(next(c_id) + '商品列表到下单支付流程')
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testdata/BusinessManager/BusinessScenario.yaml'))
    def test_business_scenario(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)