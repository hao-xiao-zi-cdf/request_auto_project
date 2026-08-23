# 风铃选品接口自动化测试项目（request_auto_project）

基于 **pytest + allure + YAML 数据驱动** 的接口自动化测试框架。测试用例全部以 YAML 文件编写，框架负责请求发送、参数关联、断言校验、数据提取、报告生成与结果通知。

## 一、框架结构

```
request_auto_project
├── base/                     # 基础类封装（测试用例执行引擎与工具）
│   ├── apiutil.py            # 核心：解析 YAML 用例、发送请求、断言、提取
│   ├── generateId.py         # 模块/用例编号生成器（M01_、C01_）
│   └── removefile.py         # 清理目录下指定后缀文件
├── common/                   # 公共方法封装
│   ├── assertions.py         # 断言实现（contains/eq/ne/rv/db）
│   ├── sendrequest.py        # requests 请求封装
│   ├── yaml_handler.py       # YAML 读写（用例数据、extract.yaml）
│   ├── debugtalk.py          # 参数传递函数库（${函数名(参数)} 的实现处）
│   ├── recordlog.py          # 日志记录（滚动日志）
│   ├── connection.py         # MySQL 连接（db 断言/数据预置用）
│   ├── dingRobot.py          # 钉钉机器人通知
│   └── feishuRobot.py        # 飞书机器人通知
├── config/                   # 全局配置目录
│   ├── setting.py            # 不随环境变化的基础参数（路径、日志级别、超时、报告类型、通知开关）
│   ├── config_test.yaml      # 随环境变化的业务数据（接口地址、数据库、机器人密钥等）
│   └── operationConfig.py    # 配置读取类
├── testdata/                 # 测试数据目录（按业务模块分子目录）
│   ├── LoginManager/         # 登录接口
│   ├── ProductManager/       # 商品/订单接口
│   ├── UserManager/          # 用户增删改查接口
│   └── BusinessManager/      # 业务场景串联用例
├── testcases/                # 测试用例文件目录
│   ├── conftest.py           # 用例级 fixture（登录、allure 环境信息、suite 标签）
│   └── test_*.py             # 各模块测试类
├── logs/                     # 测试日志目录
├── report/                   # 测试报告目录，支持两种报告
│   ├── temp/                 # allure 原始数据（--alluredir 输出）
│   └── tmreport/             # tm 风格离线 HTML 报告
├── conftest.py               # 全局操作（结果摘要通知），固定文件名不可更改
├── extract.yaml              # 接口依赖参数存放文件（接口关联的数据中转）
├── pytest.ini                # pytest 收集规则约束，固定文件名不可更改
├── requirements.txt          # 项目所用第三方库清单
└── run.py                    # 主程序入口
```

## 二、环境准备

1. **安装依赖**（建议使用镜像源）：

   ```
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **Python 版本**：3.11（框架在 3.11.9 上验证，建议使用本地 Python 环境）。

3. **Allure 命令行**：`allure` 报告服务需要本机安装 allure-commandline 并配置到 PATH，`run.py` 执行完测试后会自动调用 `allure serve report/temp` 打开报告。

4. 若运行报第三方库版本冲突，卸载报错的库后按 `requirements.txt` 重新安装即可。

## 三、运行方式

```
python run.py
```

- `config/setting.py` 中 `REPORT_TYPE = 'allure'`：运行测试 → 生成 allure 原始数据与 `report/results.xml`（junit）→ 自动打开 allure 报告
- `REPORT_TYPE = 'tm'`：生成 tm 风格 HTML 报告到 `report/tmreport/testReport.html` 并自动打开浏览器

测试结束后，根目录 `conftest.py` 的 `pytest_terminal_summary` 钩子会汇总结果，并按 `setting.py` 中的 `DD_MSG` / `FS_MSG` 开关推送钉钉 / 飞书通知（机器人 webhook 与密钥在 `config/config_test.yaml` 的 `DING_DING` / `FEI_SHU` 节）。

## 四、用例 YAML 模板

一个用例文件由若干 `baseInfo` + `testCase` 块组成，**这两个关键字不能缺少**：

```yaml
- baseInfo:
    api_name: 提交订单                 # 接口名称，用于日志与报告展示
    url: /coupApply/cms/placeAnOrder  # 只写接口路径，host 取 config_test.yaml 的 api_envi.host
    method: post                      # 请求方式
    header:
      Content-Type: application/json;charset=UTF-8
      token: ${get_extract_data(token)}   # 参数传递：取 extract.yaml 中的 token
  testCase:
    - case_name: 提交订单
      json:
        goods_id: ${get_extract_data(goodsId,0)}   # 取列表第 1 个元素
        number: 2
      validation:
        - eq: { 'message': '提交订单成功' }         # 相等断言
        - eq: { 'error_code': '0000' }
      extract:
        orderNumber: $.orderNumber                  # 提取单个值（jsonpath 或正则）
        userId: $.userId
```

### 1. baseInfo 关键字

| 关键字 | 说明 |
|---|---|
| `api_name` | 接口名称 |
| `url` | 接口路径（不含 ip 端口，host 在 `config/config_test.yaml` 的 `api_envi` 节配置） |
| `method` | 请求方式（get / post 等） |
| `header` | 请求头，按需填写 |
| `cookies` | 可选，项目需要 cookie 时才写，如 `SESSION: ${get_extract_data(cookie,SESSION)}` |

### 2. testCase 关键字

| 关键字 | 说明 |
|---|---|
| `case_name` | 用例名称 |
| `params` / `data` / `json` | 请求参数，**三者只能选一个**（见第五节） |
| `files` | 文件上传，如 `file: ./testdata/xxx.xlsx`（注意：部分导入文件接口不需要设置请求头，设置了反而报错） |
| `validation` | 断言列表（见第六节） |
| `extract` | 提取单个值，写入 `extract.yaml`（jsonpath 或正则） |
| `extract_list` | 提取多个值，以列表形式写入 `extract.yaml`（jsonpath 或正则） |

## 五、参数传递与参数类型

### 1. 参数传递

格式为 `${函数名(*args)}`，args 可有可无。函数在 `common/debugtalk.py` 中实现，常用的有：

| 函数 | 说明 |
|---|---|
| `get_extract_data(key)` | 取 `extract.yaml` 中 key 对应的值 |
| `get_extract_data(key,n)` | 当提取值是列表时：`0` 表示随机取，`1` 起按下标取 |
| `md5_encryption(x)` / `sha1_encryption(x)` / `base64_encryption(x)` | 加密 |
| `timestamp()` / `timestamp_thirteen()` | 10 位 / 13 位时间戳 |

也可自定义函数：在 `debugtalk.py` 中新增方法即可在用例里通过 `${方法名(参数)}` 调用。

### 2. 参数类型与 Content-Type 对应关系

| 场景 | 参数类型 | 对应 header |
|---|---|---|
| GET url 传参 | `params` | `application/x-www-form-urlencoded;charset=UTF-8` |
| POST 表单提交 | `data` | `application/x-www-form-urlencoded;charset=UTF-8` |
| POST JSON 提交 | `json` | `application/json;charset=UTF-8` |
| 文件上传 | `files` | `multipart/form-data; charset=utf-8` |

**参数类型一定要与接口的实际传参方式一致，对应的 header 也要同步变更。**

## 六、断言方式

`validation` 下支持以下断言，**有多种断言时 `contains` 必须写在最前面**：

```yaml
validation:
  - contains: { status_code: 200 }      # 状态码断言
  - contains: { 'message': 'success' }  # 字符串包含断言
  - contains: { 'message': None }       # 响应体为空断言
  - eq: { 'state': '已入网' }            # 相等断言（写在 contains 之后）
  - ne: { 'state': '已入网' }            # 不相等断言
  - rv: { 'data': 2 }                   # 断言响应中任意值
  - db: select * from sys_user where login_name='test999'   # 数据库断言，直接写 SQL
```

> `db` 断言依赖 `config/config_test.yaml` 中的 `MYSQL` 配置。

## 七、接口关联（extract.yaml）

- 用例通过 `extract` / `extract_list` 把响应中的值写入根目录 `extract.yaml`
- 后续用例通过 `${get_extract_data(key)}` 读取，实现接口间数据传递
- 每次会话开始时会自动清空 `extract.yaml`，写入采用"合并覆盖"方式，同名 key 只保留最新值
- jsonpath 表达式可用在线解析器调试：<http://www.atoolbox.net/Tool.php?Id=792>

## 八、测试报告

### 1. Allure 报告

- 原始数据输出到 `report/temp`，运行命令自带 `--clean-alluredir`（每次运行前清空旧数据）
- 报告的 **ENVIRONMENT** 区块由 `testcases/conftest.py` 的 `allure_environment` fixture 动态生成 `environment.properties`（中文已做 `\uXXXX` 转义，不会乱码），且生成时机在清理之后，不会被 `--clean-alluredir` 误删
- **Suites 视图**通过 `pytest_collection_modifyitems` 钩子同步为中文编号树：`项目名称 > M01_模块名（@allure.feature） > C01_用例名（@allure.story）`，编号由 `base/generateId.py` 的 `m_id` / `c_id` 生成器分配
- 若执行后报告未生成，请检查本机是否安装 allure-commandline 并加入 PATH

### 2. tm 报告

`setting.py` 中 `REPORT_TYPE = 'tm'` 时，生成 `report/tmreport/testReport.html` 离线报告并自动打开。

## 九、注意事项

1. 项目结构中的文件除 `testdata/` 下的数据文件可自由增删外，其余文件均不可删除，否则无法运行
2. `pytest.ini`、`conftest.py` 为固定文件名不可更改；`pytest.ini` 中如需注释请使用 `;` 开头，不要使用 `#` 加中文注释
3. 用例文件中引用 `testdata` 路径时使用 `./` 开头（如 `./testdata/LoginManager/login_name.yaml`），不要使用 `../`
4. 数据库功能（`testcases/conftest.py` 中的 `datadb_init`）当前为注释状态，启用后可在测试前预置数据、测试后清理数据
5. 通知机器人密钥、数据库账号等敏感信息集中在 `config/config_test.yaml`，请勿散落在代码中
