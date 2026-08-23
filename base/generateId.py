"""
Allure报告目录编号生成器

通过生成器按序产出编号，配合 @allure.feature / @allure.story 使用，
确保Allure报告中的目录顺序与pytest标记的执行顺序一致。
用法：
    @allure.feature(next(m_id) + '模块名')   # 产出 M01_、M02_...
    @allure.story(next(c_id) + '用例名')     # 产出 C01_、C02_...
"""
def generate_module_id():
    """生成模块编号：M01_, M02_, ..., M999_"""
    for i in range(1, 1000):
        yield f'M{i:02d}_'


def generate_testcase_id():
    """生成用例编号：C01_, C02_, ..., C9999_"""
    for i in range(1, 10000):
        yield f'C{i:02d}_'

m_id = generate_module_id()
c_id = generate_testcase_id()