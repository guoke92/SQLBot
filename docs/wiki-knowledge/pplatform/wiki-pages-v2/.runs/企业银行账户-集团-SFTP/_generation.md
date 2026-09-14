---FILE: tables/cust_account_info.md ---
---
type: table
title: 客户银行账户信息表
page_key: cust_account_info
domain: 企业银行账户
status: draft
aliases:
  - 客户账户信息表
  - 银行账户表
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
---

# 客户银行账户信息表

`cust_account_info` 是企业银行账户主档，承载账号、开户名、开户行、银行（总行）编码/名称等静态要素，同时承载银行小额打款认证（[[payment_auth]]）的流程状态与打款次数。账户通过 `ref_cust_company_info` 归属到企业（指向 `cust_company_info.code`，不是 id），同一归属企业内用 `default_account_flag` 维护唯一[[default_account]]。

## 需求背景

企业侧录入对公账户后需完成可用性验证：新增时同一归属企业内账号不可重复（[[account_no_unique]]）；默认还款账户在同一企业内唯一，置默认时先清旧值再置新值（[[single_default_account]]）；打款次数由 `cust_setting_config.payment_maximum_number` 初始化（[[payment_count_init]]），用尽即阻断（[[payment_count_exhausted]]）；验证金额限定在 0.01~0.99 元（[[payment_amount_range]]）；验证金额不匹配或银行库无记录时的错误次数、时间与状态存在实现与设计不一致（[[verify_fail_not_persisted]]）。

## 版本演进

- 打款认证状态由 [[bank_account_auth_state]] 描述，DB 实测出现 APPLY_00/APPLY_20/APPLY_40。
- `account_type` 存在多种写值形态（`BANK`/`OPERATION_FEE_ACCOUNT`/`received`/`1`），见 [[account_type]]。
- `status` 字段 DB 实测仅有 `INIT`，代码中未见状态迁移写值点，其完整生命周期尚不确定。
- `bank_no` 在代码中被 `setCnapsCode(bankNo)` 复用为联行号传给银行，语义被复用，使用前需确认。

```ground:table
table: cust_account_info
title: 客户银行账户信息表
fields:
  - name: id
    type: unknown
    desc: 表主键，雪花ID
    dict: null
  - name: account_no
    type: unknown
    desc: 账户账号（银行账号），新增前按该字段+归属企业去重
    dict: null
  - name: account_name
    type: unknown
    desc: 账户名称（开户名），打款申请时作为 AccountName 传给银行
    dict: null
  - name: account_type
    type: unknown
    desc: 账户类型；DB 实测主值为 'BANK'(48428)，另有 'OPERATION_FEE_ACCOUNT'(30)、'received'(1)、'1'(5)
    dict: AccountTypeEnum
  - name: default_account_flag
    type: unknown
    desc: 是否默认还款账户，'1'=默认 / '0'=非默认；同一归属企业下仅允许一条为 '1'
    dict: null
  - name: ref_cust_company_info
    type: unknown
    desc: 归属企业编码，指向 cust_company_info.code（不是 id）
    dict: null
  - name: auth_state
    type: unknown
    desc: 银行小额打款验证认证状态，DB 默认值 APPLY_00；实测分布 APPLY_00/APPLY_20/APPLY_40
    dict: AccountAuthState
  - name: payment_remaining_count
    type: unknown
    desc: 剩余可发起打款次数，由 cust_setting_config.payment_maximum_number 初始化，每次申请成功 -1
    dict: null
  - name: error_try_count
    type: unknown
    desc: 打款验证金额错误次数，result=1/2 时 +1
    dict: null
  - name: error_try_time
    type: unknown
    desc: 最后一次打款验证错误时间
    dict: null
  - name: trans_id
    type: unknown
    desc: 银行打款申请交易流水号（OriginalTxSN），申请成功后回写并用于后续查询/验证
    dict: null
  - name: trace_no
    type: unknown
    desc: 银行返回的系统跟踪号
    dict: null
  - name: bank_no
    type: unknown
    desc: 联行号；代码中同时被 setCnapsCode(bankNo) 复用为联行号传给银行，语义被复用
    dict: null
  - name: bank_code
    type: unknown
    desc: 银行(总行)代码
    dict: null
  - name: bank_code_name
    type: unknown
    desc: 银行(总行)名称，打款申请时作为 BankName 传给银行
    dict: null
  - name: bank_branch_name
    type: unknown
    desc: 账户开户行
    dict: null
  - name: status
    type: unknown
    desc: 账户状态；DB 实测仅有 'INIT'，代码中未见状态迁移写值点
    dict: null
  - name: receive_payment_type
    type: unknown
    desc: 收付类型
    dict: null
  - name: enable
    type: unknown
    desc: 逻辑启用标识，DB 全量 'Y'
    dict: null
  - name: main_data_id
    type: unknown
    desc: 主数据id
    dict: null
```
---END FILE---

---FILE: tables/cust_group_rel.md ---
---
type: table
title: 集团成员单位关系表
page_key: cust_group_rel
domain: 集团关系
status: draft
aliases:
  - 集团关系表
  - 成员单位关系表
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
---

# 集团成员单位关系表

`cust_group_rel` 描述集团与其成员单位之间的树形关系：一行记录代表“当前成员企业（`cust_id`）”上挂到“上一级企业（`parent_cust_id`）”的那条关系，同时冗余根集团企业（`root_cust_id`）与根节点（`root_group_id`）用于整树检索。`parent_group_id`/`root_group_id` 自引用本表 `id`，建树时按 `parent_group_id` 分组。

## 需求背景

集团关系需要支持多级建树与按根节点拉平（`listAllNodesByRootId`）、按 `db_tenant_code` 做租户隔离。成员单位关系的生效依赖签署流程：新增关系先落未生效（[[cust_group_rel_status]]），发送签署待办（[[notice_no_duplicate]]、[[async_notice_tolerant]]）；根节点不允许再签署/拒绝（[[root_group_no_operation]]）；删除成员单位前必须做在途业务校验（[[member_remove_check_business]]）；导入时同一上级下成员单位角色必须一致（[[member_role_consistency]]）。

## 版本演进

- `cust_type` 以 JSON 数组字符串落库（代码用 `JSONArray.toJSONString()` 写入，形如 `["CORE"]`），支持多角色逐条写入，见 [[enterprise_role]]。
- `level` 代码仅在根节点写入 `1`，DB 实测仅出现 `'1'`；`root_flag='Y'` 29 条与 `level=1` 的 29 条一致。
- 关系状态取值为 EFFECTIVE/INEFFECTIVE/REJECTED，见 [[cust_group_rel_status]]。
- 需求文档另有“企业状态流转：待提交→审核中→已通过；已通过→已冻结/已注销”的主张，代码侧未被证实，见 [[cust_group_rel_status]] 版本演进说明。

```ground:table
table: cust_group_rel
title: 集团成员单位关系表
fields:
  - name: id
    type: unknown
    desc: 表主键，集团关系树节点ID
    dict: null
  - name: cust_id
    type: unknown
    desc: 当前成员企业ID，指向 cust_company_info.id
    dict: null
  - name: parent_cust_id
    type: unknown
    desc: 上一级企业ID，指向 cust_company_info.id
    dict: null
  - name: parent_group_id
    type: unknown
    desc: 父节点ID，指向本表 cust_group_rel.id，建树时按此分组
    dict: null
  - name: root_cust_id
    type: unknown
    desc: 根集团企业ID，指向 cust_company_info.id
    dict: null
  - name: root_group_id
    type: unknown
    desc: 根节点ID，指向本表 cust_group_rel.id，用于 listAllNodesByRootId
    dict: null
  - name: root_flag
    type: unknown
    desc: 是否集团根企业，'Y'=是 / 'N'=不是；DB root_flag='Y' 29 条与 level=1 的 29 条一致
    dict: null
  - name: level
    type: unknown
    desc: 层级；代码仅在根节点写入 1，DB 实测仅出现 '1'
    dict: null
  - name: cust_type
    type: unknown
    desc: 企业角色，JSON 数组字符串（代码用 JSONArray.toJSONString() 写入，形如 ["CORE"]），支持多角色遍历写入
    dict: null
  - name: status
    type: unknown
    desc: 关系生效状态：EFFECTIVE/INEFFECTIVE/REJECTED
    dict: null
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识，DB 实测 17 个取值，是集团关系查询的关键过滤条件
    dict: null
```
---END FILE---

---FILE: tables/cust_sftp.md ---
---
type: table
title: 渠道 SFTP 配置表
page_key: cust_sftp
domain: SFTP 渠道
status: draft
aliases:
  - SFTP配置表
  - 渠道SFTP配置
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
---

# 渠道 SFTP 配置表

`cust_sftp` 保存各渠道方文件交换所用的 SFTP 连接配置：渠道编码（`channel`）、主机（`host`）、端口（`port`）、登录账号（`user_name`）、渠道中文名（`name`）与数据租户标识（`db_tenant_code`）。`channel` 在实测数据中 16 条互不相同，是配置的唯一业务键。

## 需求背景

不同渠道方（如天合光能、深天马、百果园、美团）各自需要独立的 SFTP 主机与账号，凭 [[sftp_channel]] 定位配置；`db_tenant_code` 用于租户级隔离，与渠道不是一一对应关系。

## 版本演进

- 实测 `host` 仅出现 `qa.sftp.lls.com`(15) / `uat.sftp.lls.com`(1)，仍以测试环境地址为主。
- 实测 `port` 全部为 `'22'`，`enable` 全部为 `'Y'`。
- `db_tenant_code` 与 `channel` 非一一对应（`ISOLATE_TAG_zjsj`、`sny` 各有 2 条），按渠道统计与按租户统计口径不同。

```ground:table
table: cust_sftp
title: 渠道 SFTP 配置表
fields:
  - name: channel
    type: unknown
    desc: SFTP 渠道编码（如 ZTSJ、tianma、meituan、sny_test），DB 16 条互不相同
    dict: null
  - name: host
    type: unknown
    desc: SFTP 主机地址，实测 qa.sftp.lls.com(15) / uat.sftp.lls.com(1)
    dict: null
  - name: port
    type: unknown
    desc: SFTP 端口，实测全部 '22'
    dict: null
  - name: user_name
    type: unknown
    desc: SFTP 登录账号，命名形如 app_<渠道>_<日期序列>
    dict: null
  - name: name
    type: unknown
    desc: 渠道中文名称（如 天合光能、深天马、百果园、美团）
    dict: null
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识，与 channel 非一一对应（ISOLATE_TAG_zjsj、sny 各有 2 条）
    dict: null
  - name: enable
    type: unknown
    desc: 是否启用，实测全部 'Y'
    dict: null
```
---END FILE---

---FILE: enums/account_type.md ---
---
type: enum
title: 账户类型 account_type
page_key: account_type
domain: 企业银行账户
status: draft
aliases:
  - AccountTypeEnum
  - 账户类型枚举
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
---

# 账户类型 account_type

`cust_account_info.account_type` 描述账户性质，对应 `AccountTypeEnum`。同一枚举值在代码中存在两种键形态：`name()`（如 `BANK`）与 `getDictParam()` 的数字形态（如 `1`），DB 中两种形态并存，写值点需逐个确认。

## 需求背景

账户类型是账户统计的主口径之一：`BANK` 占 48428/48468，另有运营费账户、收款账户等少量取值，按类型统计时若只按 `BANK` 过滤会漏掉运营费账户口径（[[bank_account_type]]）。

## 版本演进

- `BANK` 为绝对主值（48428 条），与 `.name()` 落库一致。
- `received` 仅 1 条，属低频写入路径（`getDictKey()`）。
- `'1'` 仅 5 条，为数字形态遗留；同值存在 `getDictParam=1` 与 `name()=BANK` 两种键，说明主路径是 `name()`。
- `OPERATION_FEE_ACCOUNT` 30 条，代码枚举基线完全未声明，需补枚举，否则按 `account_type` 统计会漏口径。

```ground:enum
field: cust_account_info.account_type
values:
  - value: BANK
    java_name: AccountTypeEnum.BANK
    stored_as: name()/字面量 'BANK'
    label: 银行
    verdict: confirm
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/CustPersonController.java:305
    note: DB 实测 48428 条为字面 'BANK'，与 .name() 落库一致，底稿 stored_as=name 成立
  - value: received
    java_name: AccountTypeEnum.RECEIVED
    stored_as: getDictKey()
    label: 收款
    verdict: confirm
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/enums/AccountTypeEnum.java
    note: DB 仅 1 条，accessors 声明 getDictKey=1 处被引用，属低频写入路径
  - value: "1"
    java_name: AccountTypeEnum.BANK.getDictParam()
    stored_as: dictParam 数字形态
    label: 银行（数字形态）
    verdict: correct
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/enums/AccountTypeEnum.java
    note: 枚举同值存在 getDictParam=1 与 name()=BANK 两种键；DB 中 '1' 仅 5 条、'BANK' 48428 条，说明主路径是 name()，'1' 为历史/其他写入点遗留，底稿未体现键混用
  - value: OPERATION_FEE_ACCOUNT
    java_name: null
    stored_as: 字面量
    label: 运营费账户
    verdict: correct
    evidence: db
    note: DB 30 条，代码枚举基线完全未声明，需补枚举，否则按 account_type 统计会漏口径
```
---END FILE---

---FILE: enums/auth_state.md ---
---
type: enum
title: 打款认证状态 auth_state
page_key: auth_state
domain: 企业银行账户
status: draft
aliases:
  - AccountAuthState
  - 认证状态枚举
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
---

# 打款认证状态 auth_state

`cust_account_info.auth_state` 的枚举为 `AccountAuthState`，取值形如 `APPLY_00`~`APPLY_40`，状态迁移见 [[bank_account_auth_state]]。审计发现同一枚举“写值用 `getDictParam()`、查询用 `getDictKey()`”，存在键形态混用风险，需确认存储形态。

## 需求背景

该字段是[[payment_auth]]流程的阶段标记，决定账户能否继续发起打款、能否进入金额验证，也是[[not_applied_payment_auth]]与“已完成验证”口径的依据。

## 版本演进

- `APPLY_00` 为 DB 列默认值，占 49144 条，是存量主状态。
- `APPLY_20`、`APPLY_40` 已在生产数据出现；`APPLY_10`、`APPLY_30` 仅在代码常量中出现。
- `APPLY_10` 的审计结论为 reject：写值点用 `getDictParam()`、查询点用 `getDictKey()`，键形态不一致，审计备注在给定材料中被截断。

```ground:enum
field: cust_account_info.auth_state
values:
  - value: APPLY_10
    java_name: AccountAuthState.APPLY_10
    stored_as: 写值用 getDictParam()、查询用 getDictKey()
    label: 打款申请已提交
    verdict: reject
    evidence: CustAccountApplication.java:193（getDictParam） vs CustAccountApplication.java:222（getDictKey）
    note: 同一枚举写值与查询使用了不同的键取法，存在键形态混用风险；审计备注在语义分析中被截断，需回源码确认落库形态
```
---END FILE---

---FILE: processes/bank_account_auth_state.md ---
---
type: process
title: 银行账户打款认证状态
page_key: bank_account_auth_state
domain: 企业银行账户
status: draft
aliases:
  - 打款认证状态机
  - auth_state 状态机
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
---

# 银行账户打款认证状态

`cust_account_info.auth_state` 的生命周期：初始 `APPLY_00` → 发起小额打款申请进入 `APPLY_10` → 银行受理成功 `APPLY_20`（或受理失败 `APPLY_30`）→ 验证金额一致落 `APPLY_40`。字段枚举见 [[auth_state]]，业务术语见 [[payment_auth]]。

## 需求背景

账户须通过银行小额打款验证方可确认可用：申请前受打款次数约束（[[payment_count_exhausted]]、[[payment_count_init]]），验证金额受区间校验（[[payment_amount_range]]），验证失败分支存在不落库问题（[[verify_fail_not_persisted]]）。初始态口径见 [[not_applied_payment_auth]]。

## 版本演进

- `APPLY_00`（DB 列默认）与 `APPLY_20`/`APPLY_40` 出现在生产数据；`APPLY_10`/`APPLY_30` 见于代码常量。
- 查询打款结果 `status=10` 时幂等重写为 `APPLY_10`。
- `result=1/2` 两条迁移指向 `APPLY_40`，但实现中先抛异常、状态不落库，迁移实际不成立。

```ground:process
name: 银行账户打款认证状态
field: cust_account_info.auth_state
states:
  - value: APPLY_00
    label: 初始，未发起打款认证（DB 列默认值）
    source: db_dist
  - value: APPLY_10
    label: 已提交打款申请、待银行受理
    source: code_const
  - value: APPLY_20
    label: 银行受理成功（允许发起金额验证）
    source: code_const
  - value: APPLY_30
    label: 申请打款受理失败
    source: code_const
  - value: APPLY_40
    label: 已完成验证（金额一致时落库）
    source: db_dist
transitions:
  - from: APPLY_00
    event: 发起小额打款申请 cnapsPaymentApply
    to: APPLY_10
    evidence: code_path:CustAccountApplication.java:193
  - from: APPLY_10
    event: 查询打款结果 status=10（幂等重写）
    to: APPLY_10
    evidence: code_path:CustAccountApplication.java:222
  - from: APPLY_10
    event: 查询打款结果 status=20
    to: APPLY_20
    evidence: code_path:CustAccountApplication.java:224
  - from: APPLY_10
    event: 查询打款结果 status=30
    to: APPLY_30
    evidence: code_path:CustAccountApplication.java:226
  - from: APPLY_20
    event: 打款验证金额一致 result=0
    to: APPLY_40
    evidence: code_path:CustAccountApplication.java:283
  - from: APPLY_20
    event: 打款验证金额不匹配 result=1（抛异常，状态未落库）
    to: APPLY_40
    evidence: code_path:CustAccountApplication.java:287
  - from: APPLY_20
    event: 银行库无记录 result=2（抛异常，状态未落库）
    to: APPLY_40
    evidence: code_path:CustAccountApplication.java:293
```
---END FILE---

---FILE: processes/cust_group_rel_status.md ---
---
type: process
title: 集团成员单位关系状态
page_key: cust_group_rel_status
domain: 集团关系
status: draft
aliases:
  - 集团关系状态机
  - 成员单位生效状态
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
---

> (document_claim，未证实)

# 集团成员单位关系状态

`cust_group_rel.status` 描述成员单位关系的生效状态：新增/待办发出后为 `INEFFECTIVE`，成员单位签署协议 `accept` 后置 `EFFECTIVE`，拒绝 `reject` 后置 `REJECTED`；集团根企业的关系在建档成功场景下可直接落 `EFFECTIVE`。

## 需求背景

关系生效是集团业务的前置条件：查询成员只返回 `EFFECTIVE` 节点（[[effective_group_rel]]），根节点禁止再次签署或拒绝（[[root_group_no_operation]]），签署待办不可重复发送且异步容错（[[notice_no_duplicate]]、[[async_notice_tolerant]]），删除成员单位前需校验在途业务（[[member_remove_check_business]]）。

## 版本演进

- 新增关系（`addExistSubCustGroupRel`/`addNewSubCustGroupRel`/导入）与发送签署待办均落 `INEFFECTIVE`。
- `effectGroupRel` 外部回调可把 `INEFFECTIVE` 置为 `EFFECTIVE`。
- 需求文档主张“企业状态流转：待提交→审核中→已通过；已通过→已冻结/已注销”。**该主张为 document_claim，未证实**：代码侧仅见 `CustBuildStatusEnum` 的 BUILD_SUCCESS/CUST_BUILDING/BUILD_FAIL/CUST_CHANGE 被引用，冻结/注销流转的枚举与写值点未出现在给出的文件中。

```ground:process
name: 集团成员单位关系状态
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效
    source: code_enum
  - value: EFFECTIVE
    label: 已生效
    source: db_dist
  - value: REJECTED
    label: 已拒绝
    source: code_enum
transitions:
  - from: null
    event: 新增成员单位关系（addExistSubCustGroupRel/addNewSubCustGroupRel/导入）
    to: INEFFECTIVE
    evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - from: null
    event: 发送成员单位签署待办 sendCustGroupRelNotice
    to: INEFFECTIVE
    evidence: code_path:CustGroupLicenseApplication.java:sendCustGroupRelNotice
  - from: INEFFECTIVE
    event: 成员单位签署协议 accept
    to: EFFECTIVE
    evidence: code_path:CustGroupLicenseApplication.java:accept
  - from: INEFFECTIVE
    event: 拒绝签署协议 reject
    to: REJECTED
    evidence: code_path:CustGroupLicenseApplication.java:reject
  - from: null
    event: 新增集团根企业且企业已建档成功 BUILD_SUCCESS
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java:addExistRootGroupRel
  - from: INEFFECTIVE
    event: effectGroupRel 外部回调置为已生效
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java:effectGroupRel
```
---END FILE---

---FILE: calibers/default_repayment_account.md ---
---
type: caliber
title: 默认还款账户
page_key: default_repayment_account
domain: 企业银行账户
status: draft
aliases:
  - 默认账户口径
  - 默认还款账号
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 默认还款账户

口径判断：`cust_account_info.default_account_flag = '1'`。语义为同一归属企业（`ref_cust_company_info`）下唯一的默认还款账户，由置默认与保存后逻辑互斥维护，术语辨析见 [[default_account]]。

## 需求背景

还款/扣款类业务需要明确“用哪个账户”，因此要求单企业唯一默认账户（[[single_default_account]]）。

## 版本演进

- 该口径由 `setDefaultFlag`/`afterSave` 维护，属写时维护型口径，不是查询时推导。

```ground:caliber
name: 默认还款账户
predicate: cust_account_info.default_account_flag = '1'
scope: 同一 ref_cust_company_info 下唯一；setDefaultFlag/afterSave 维护
evidence: code_path:CustAccountApplication.java:setDefaultFlag
```
---END FILE---

---FILE: calibers/valid_account.md ---
---
type: caliber
title: 有效账户
page_key: valid_account
domain: 企业银行账户
status: draft
aliases:
  - 启用账户口径
  - enable=Y
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
---

# 有效账户

口径判断：`cust_account_info.enable = 'Y'`，即逻辑启用标识为启用的账户。

## 需求背景

账户使用范围统计以启用标识收口，停用账户不纳入可用账户集合。

## 版本演进

- 全表实测均为 `'Y'`，该口径目前不产生过滤差异；一旦出现 `'N'`，需确认是否配套停用功能与迁移写值点。

```ground:caliber
name: 有效账户
predicate: cust_account_info.enable = 'Y'
scope: 全表实测均为 Y
evidence: db
```
---END FILE---

---FILE: calibers/bank_account_type.md ---
---
type: caliber
title: 银行账户（账户类型）
page_key: bank_account_type
domain: 企业银行账户
status: draft
aliases:
  - account_type=BANK
  - 银行账户口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
---

# 银行账户（账户类型）

口径判断：`cust_account_info.account_type = 'BANK'`，是账户类型的主口径。

## 需求背景

账户类型统计与筛选需要区分银行账户与运营费账户、收款账户，取值审计见 [[account_type]]。

## 版本演进

- `BANK` 占 48428/48468，为主口径；`OPERATION_FEE_ACCOUNT`(30)、`received`(1)、`'1'`(5) 为少数取值，按 `BANK` 过滤时会漏掉这些账户。

```ground:caliber
name: 银行账户（账户类型）
predicate: cust_account_info.account_type = 'BANK'
scope: 占 48428/48468，是账户类型主口径
evidence: db
```
---END FILE---

---FILE: calibers/not_applied_payment_auth.md ---
---
type: caliber
title: 未发起打款认证
page_key: not_applied_payment_auth
domain: 企业银行账户
status: draft
aliases:
  - auth_state=APPLY_00
  - 未认证账户口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
---

# 未发起打款认证

口径判断：`cust_account_info.auth_state = 'APPLY_00'`，即尚未发起打款认证的账户。

## 需求背景

用于识别待认证账户存量，是[[payment_auth]]流程的起始集合，状态迁移见 [[bank_account_auth_state]]。

## 版本演进

- 该值为 DB 列默认值，占 49144 条，是存量账户的绝对主状态。

```ground:caliber
name: 未发起打款认证
predicate: cust_account_info.auth_state = 'APPLY_00'
scope: DB 列默认值，占 49144 条
evidence: db
```
---END FILE---

---FILE: calibers/effective_group_rel.md ---
---
type: caliber
title: 已生效集团关系
page_key: effective_group_rel
domain: 集团关系
status: draft
aliases:
  - status=EFFECTIVE
  - 生效成员单位口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 已生效集团关系

口径判断：`cust_group_rel.status = 'EFFECTIVE'`，即签署完成、关系已生效的集团成员单位关系。

## 需求背景

集团成员查询 `listSubCust` 仅返回该状态节点，未生效/已拒绝关系不进入成员视图，状态来源见 [[cust_group_rel_status]]、术语见 [[member_unit]]。

## 版本演进

- 生效可由 `accept` 签署、根企业建档成功、`effectGroupRel` 外部回调三条路径达成，落地路径较多，排查成员缺失时需同时看签署与回调。

```ground:caliber
name: 已生效集团关系
predicate: cust_group_rel.status = 'EFFECTIVE'
scope: listSubCust 仅返回该状态节点
evidence: code_path:CustGroupRelApplication.java:listSubCust
```
---END FILE---

---FILE: calibers/group_root_node.md ---
---
type: caliber
title: 集团根节点
page_key: group_root_node
domain: 集团关系
status: draft
aliases:
  - root_flag=Y
  - 根企业口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 集团根节点

口径判断：`cust_group_rel.root_flag = 'Y'`，即集团根企业所在的关系节点。

## 需求背景

根节点是集团树的树根，也是签署流程的边界：`checkCustGroup` 拒绝对根节点做签署/拒绝操作（[[root_group_no_operation]]）。术语辨析见 [[group_root]]。

## 版本演进

- DB `root_flag='Y'` 29 条与 `level=1` 的 29 条一致，当前两者可作为同一批节点的双重判据。

```ground:caliber
name: 集团根节点
predicate: cust_group_rel.root_flag = 'Y'
scope: checkCustGroup 拒绝对根节点做签署/拒绝操作
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```
---END FILE---

---FILE: concepts/default_account.md ---
---
type: concept
title: 默认账户
page_key: default_account
domain: 企业银行账户
status: draft
aliases:
  - 默认还款账号
  - 默认还款账户
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_account_info.default_account_flag
field_targets:
  - cust_account_info.default_account_flag
also_confused_with:
  - cust_account_info.account_type
adjudication: boundary
---

# 默认账户

业务上指企业用于默认还款的那一个银行账户，落库为 `cust_account_info.default_account_flag = '1'`，口径见 [[default_repayment_account]]。

## 需求背景

企业可维护多个账户，但还款类业务只认“默认”那一个，因此需要唯一的默认标记与置默认操作（[[single_default_account]]）。

## 版本演进

- 默认标记由写时互斥维护（`setDefaultFlag`/`afterSave`），不是查询时按时间或类型推导。

## 边界（adjudication: boundary）

`default_account_flag` 是企业维度内的默认标记，由 `setDefaultFlag`/`afterSave` 互斥维护；`account_type` 描述账户性质（银行/运营费账户），二者不可互推。统计“默认账户数”必须用 `default_account_flag`，不能用 `account_type`。
---END FILE---

---FILE: concepts/group_root.md ---
---
type: concept
title: 集团（集团公司/根企业）
page_key: group_root
domain: 集团关系
status: draft
aliases:
  - root
  - rootGroup
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_group_rel.root_flag
field_targets:
  - cust_group_rel.root_flag
also_confused_with:
  - cust_company_info.cust_company_type
adjudication: boundary
---

# 集团（集团公司/根企业）

口语中的“集团/根企业”在数据上通常指 `cust_group_rel.root_flag = 'Y'` 的关系节点，口径见 [[group_root_node]]。

## 需求背景

集团树的构建、成员查询与签署边界都以根节点为起点：根节点禁止再次签署/拒绝（[[root_group_no_operation]]），按根节点拉平整树用于删除前校验（[[member_remove_check_business]]）。

## 版本演进

- 代码 `showCustGroupTree` 先看企业角色再查关系，说明“是集团”这一判断在实现中由角色与关系联合决定。

## 边界（adjudication: boundary）

`root_flag='Y'` 是关系表上的根节点标记；`cust_company_info.cust_company_type` 含 `CORPORATION_COMPANY` 才是企业角色意义上的集团。`showCustGroupTree` 先看角色再查关系，二者需联合判断，不可互推。
---END FILE---

---FILE: concepts/member_unit.md ---
---
type: concept
title: 成员单位
page_key: member_unit
domain: 集团关系
status: draft
aliases:
  - 子企业
  - 子级企业
  - 上级企业
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_group_rel.cust_id
field_targets:
  - cust_group_rel.cust_id
also_confused_with:
  - cust_group_rel.parent_cust_id
adjudication: boundary
---

# 成员单位

集团关系中的“成员单位”指当前这条关系挂靠的企业，落库为 `cust_group_rel.cust_id`；其上一级企业为 `parent_cust_id`。

## 需求背景

成员单位的增删改查、签署待办、删除前在途校验都围绕 `cust_id` 展开（[[member_remove_check_business]]、[[notice_no_duplicate]]），角色一致性校验见 [[member_role_consistency]]。

## 版本演进

- 关系表同时冗余 `root_cust_id`/`root_group_id`，成员查询可按根节点一次性拉平，减少递归。

## 边界（adjudication: boundary）

`cust_id` 是当前成员企业，`parent_cust_id` 是其上一级企业；两者同层级语义相反，建树/校验必须区分。口语中“上级企业”“子企业”在需求文档里都出现过，落到字段前必须先确认方向。
---END FILE---

---FILE: concepts/enterprise_role.md ---
---
type: concept
title: 企业角色
page_key: enterprise_role
domain: 集团关系
status: draft
aliases:
  - custType
  - companyType
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
maps_to: cust_group_rel.cust_type
field_targets:
  - cust_group_rel.cust_type
also_confused_with:
  - cust_company_info.cust_company_type
adjudication: boundary
---

# 企业角色

关系维度上的企业角色落库为 `cust_group_rel.cust_type`，是 JSON 数组字符串（形如 `["CORE"]`），支持一条关系多角色逐条写入。

## 需求背景

角色决定成员单位在集团中的定位，导入时要求同一上级下所有成员单位角色一致，且与已存在上级企业角色一致（[[member_role_consistency]]）。

## 版本演进

- `cust_type` 采用 JSON 数组字符串存储而非单值，历史上支持过多角色；解析统计时需按数组处理。

## 边界（adjudication: boundary）

`cust_group_rel.cust_type` 限定该条关系下的角色（JSON 数组字符串，多角色逐条写入），`cust_company_info.cust_company_type` 是企业全局角色；导入校验要求两者一致，但两者不是同一个字段、也不总是同时存在。
---END FILE---

---FILE: concepts/payment_auth.md ---
---
type: concept
title: 打款验证
page_key: payment_auth
domain: 企业银行账户
status: draft
aliases:
  - 小额打款
  - 打款认证
  - 打款验证码
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
maps_to: cust_account_info.auth_state
field_targets:
  - cust_account_info.auth_state
also_confused_with:
  - cust_account_info.status
adjudication: boundary
---

# 打款验证

业务上指银行小额打款认证：向企业账户打入随机小额资金，由企业回填金额以确认账户可用。流程阶段落库在 `cust_account_info.auth_state`，取值见 [[auth_state]]，迁移见 [[bank_account_auth_state]]。

## 需求背景

账户验证受打款次数约束（[[payment_count_init]]、[[payment_count_exhausted]]）与金额区间约束（[[payment_amount_range]]）；验证失败的错误次数与状态存在不落库问题（[[verify_fail_not_persisted]]）。

## 版本演进

- 验证相关字段 `trans_id`（OriginalTxSN）、`trace_no` 由银行回写，用于后续查询与验证。
- `error_try_count`/`error_try_time` 在失败分支被设置，但因异常提前抛出且方法无事务注解，实际可能不持久化。

## 边界（adjudication: boundary）

`auth_state` 描述打款认证流程阶段（`APPLY_xx`）；`status` 是账户业务状态，DB 实测仅 `INIT`，代码无迁移。两者不可互推：账户“状态正常”不代表“打款已验证”。
---END FILE---

---FILE: concepts/sftp_channel.md ---
---
type: concept
title: SFTP 渠道
page_key: sftp_channel
domain: SFTP 渠道
status: draft
aliases:
  - channel
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
maps_to: cust_sftp.channel
field_targets:
  - cust_sftp.channel
also_confused_with:
  - cust_sftp.db_tenant_code
adjudication: boundary
---

# SFTP 渠道

“渠道”指文件交换的对接方编码，落库为 `cust_sftp.channel`（如 ZTSJ、tianma、meituan、sny_test），是 SFTP 配置的唯一业务键。

## 需求背景

不同渠道方的文件交互需要各自独立的 SFTP 主机与账号，凭渠道编码定位配置，配置表见 [[cust_sftp]]。

## 版本演进

- 实测 16 条 `channel` 互不相同，`host` 仍以 QA 环境地址为主。

## 边界（adjudication: boundary）

`channel` 是业务渠道编码（ZTSJ/tianma/meituan），`db_tenant_code` 是数据租户标识；两者取值域不同且非一一对应（`ISOLATE_TAG_zjsj`、`sny` 各有 2 条），按渠道统计与按租户统计结论会不同。
---END FILE---

---FILE: rules/account_no_unique.md ---
---
type: rule
title: 账户不可重复添加
page_key: account_no_unique
domain: 企业银行账户
status: draft
aliases:
  - 账号去重规则
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 账户不可重复添加

新增账户前，在同一归属企业内校验 `account_no` 是否已存在，命中即拒绝并提示“账户不能重复添加”。

## 需求背景

账户档案需要避免同一企业下重复登记同一银行账号，否则默认账户、打款次数、认证状态会出现多条并行记录。表结构见 [[cust_account_info]]。

## 版本演进

- 校验在 `checkBefore` 中完成，属前置校验，非数据库唯一约束。

```ground:rule
name: 账户不可重复添加
content: 同一归属企业内相同 account_no 唯一，命中时报“账户不能重复添加”
impact: 阻断新增
field_targets:
  - cust_account_info.account_no
  - cust_account_info.ref_cust_company_info
evidence: code_path:CustAccountApplication.java:checkBefore
```
---END FILE---

---FILE: rules/single_default_account.md ---
---
type: rule
title: 单企业唯一默认账户
page_key: single_default_account
domain: 企业银行账户
status: draft
aliases:
  - 默认账户互斥规则
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 单企业唯一默认账户

置默认时先把该企业已有 `default_account_flag='1'` 的账户改为 `'0'`，再把当前账户置 `'1'`，保证同一企业下仅一条默认。

## 需求背景

还款类业务只认唯一默认账户，口径见 [[default_repayment_account]]、术语见 [[default_account]]。

## 版本演进

- 由写时更新实现（先清后置），非数据库唯一索引；并发置默认时需确认是否互斥。

```ground:rule
name: 单企业唯一默认账户
content: 置默认时先把该企业已有 default_account_flag='1' 的账户改为 '0'，再把当前账户置 '1'
impact: 更新存量数据
field_targets:
  - cust_account_info.default_account_flag
evidence: code_path:CustAccountApplication.java:setDefaultFlag
```
---END FILE---

---FILE: rules/payment_count_init.md ---
---
type: rule
title: 打款次数初始化
page_key: payment_count_init
domain: 企业银行账户
status: draft
aliases:
  - payment_remaining_count 初始化规则
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 打款次数初始化

从 `cust_setting_config.payment_maximum_number` 取首条配置，写入账户的 `payment_remaining_count`，作为该账户可发起打款次数的起点。

## 需求背景

打款验证的调用次数需要受控，次数上限走配置而非硬编码，见 [[payment_auth]]、[[payment_count_exhausted]]。

## 版本演进

- 取“首条配置”意味着配置表存在多条时以第一条为准，后续若配置分租户/分渠道，需要重新确认取数逻辑。

```ground:rule
name: 打款次数初始化
content: 从 cust_setting_config.payment_maximum_number 取首条配置写入 payment_remaining_count
impact: 初始化字段
field_targets:
  - cust_account_info.payment_remaining_count
  - cust_setting_config.payment_maximum_number
evidence: code_path:CustAccountApplication.java:updatePayCount
```
---END FILE---

---FILE: rules/payment_count_exhausted.md ---
---
type: rule
title: 打款次数用尽阻断
page_key: payment_count_exhausted
domain: 企业银行账户
status: draft
aliases:
  - 打款次数用完阻断
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 打款次数用尽阻断

`payment_remaining_count == 0` 时抛“今天打款次数已用完”，阻断打款申请；申请成功后剩余次数 -1。

## 需求背景

打款涉及真实资金与银行接口成本，需要对单账户的发起次数做上限控制，初始化规则见 [[payment_count_init]]。

## 版本演进

- 提示文案为“今天打款次数已用完”，但字段语义是“剩余可发起次数”并随申请递减，未见到按日重置逻辑的写值点，日切语义待确认。

```ground:rule
name: 打款次数用尽阻断
content: payment_remaining_count == 0 时抛“今天打款次数已用完”，申请成功后 -1
impact: 阻断
field_targets:
  - cust_account_info.payment_remaining_count
evidence: code_path:CustAccountApplication.java:cnapsPaymentApply
```
---END FILE---

---FILE: rules/payment_amount_range.md ---
---
type: rule
title: 打款验证金额区间
page_key: payment_amount_range
domain: 企业银行账户
status: draft
aliases:
  - 验证金额校验
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 打款验证金额区间

验证金额须 >0 且 <1（0.01~0.99 元），控制器换算为“分”后传给银行。

## 需求背景

小额打款验证要求金额足够小，避免企业误当成正常回款；单位换算发生在控制器层，接口文档与页面提示需与之一致。

## 版本演进

- 入参以元为单位、出参以分为单位，跨层单位不一致是排查打款金额不符的常见来源。

```ground:rule
name: 打款验证金额区间
content: 验证金额须 >0 且 <1（0.01~0.99），控制器换算为分后传银行
impact: 入参校验
field_targets:
  - cust_account_info.trans_id
evidence: code_path:CustAccountInfoController.java:checkAmount
```
---END FILE---

---FILE: rules/verify_fail_not_persisted.md ---
---
type: rule
title: 验证失败不落库
page_key: verify_fail_not_persisted
domain: 企业银行账户
status: draft
aliases:
  - 打款验证失败状态未持久化
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 验证失败不落库

`result=1/2` 分支在 `setErrorTryCount`/`setErrorTryTime` 之后、`saveOrUpdate` 之前直接 `throw`，且方法无事务注解，错误次数与 `APPLY_40` 实际不会持久化，属实现与设计不一致。

## 需求背景

设计意图是记录失败次数与时间（`error_try_count`/`error_try_time`）以便风控与运营跟进，同时把状态推进到 `APPLY_40`；实现上失败分支提前抛出，导致状态机中两条指向 `APPLY_40` 的迁移（见 [[bank_account_auth_state]]）实际不成立，[[auth_state]] 的失败态观测缺失。

## 版本演进

- 该问题当前未修复：无事务包裹 + 提前 throw，错误计数与状态写入同时丢失。
- 排查“失败次数不增长”“验证失败后状态仍是 APPLY_20”类问题时，应首先怀疑本规则。

```ground:rule
name: 验证失败不落库
content: result=1/2 分支在 setErrorTryCount/setErrorTryTime 之后、saveOrUpdate 之前直接 throw，且方法无事务注解，错误次数与 APPLY_40 实际不会持久化
impact: 实现与设计不一致
field_targets:
  - cust_account_info.error_try_count
  - cust_account_info.error_try_time
  - cust_account_info.auth_state
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```
---END FILE---

---FILE: rules/root_group_no_operation.md ---
---
type: rule
title: group根企业禁操作
page_key: root_group_no_operation
domain: 集团关系
status: draft
aliases:
  - 根节点禁止签署
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# group根企业禁操作

`root_flag='Y'` 或状态已 `EFFECTIVE` 的集团关系，不允许再次执行 accept/reject。

## 需求背景

根企业自身不存在“被上级邀请签署”的场景，已生效关系重复签署也会造成状态回退，因此需要前置拦截，见 [[group_root_node]]、[[effective_group_rel]]、[[cust_group_rel_status]]。

## 版本演进

- 拦截在 `checkCustGroup` 中完成，属应用层校验；直接调用底层状态更新接口不受此约束。

```ground:rule
name: group根企业禁操作
content: root_flag='Y' 或状态已 EFFECTIVE 的集团关系不允许再次 accept/reject
impact: 阻断
field_targets:
  - cust_group_rel.root_flag
  - cust_group_rel.status
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```
---END FILE---

---FILE: rules/notice_no_duplicate.md ---
---
type: rule
title: 待办不可重复发送
page_key: notice_no_duplicate
domain: 集团关系
status: draft
aliases:
  - 签署待办防重复
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 待办不可重复发送

`queryLatelyNotice` 命中未处理待办时抛“企业存在未办理的待办事项，不支持重复发送”，阻断再次发起签署待办。

## 需求背景

成员单位签署待办（[[member_unit]]、[[cust_group_rel_status]]）重复推送会干扰用户并可能产生多份签署记录，因此要求同一关系上同一时刻只有一条未办理待办。

## 版本演进

- 判重依赖“最近待办”查询结果，未见到按关系 ID 的唯一约束，历史脏待办可能造成长期阻断。

```ground:rule
name: 待办不可重复发送
content: queryLatelyNotice 命中未处理待办时抛“企业存在未办理的待办事项，不支持重复发送”
impact: 阻断
field_targets:
  - cust_group_rel.id
evidence: code_path:CustGroupLicenseApplication.java:sendCustGroupRelNotice
```
---END FILE---

---FILE: rules/member_remove_check_business.md ---
---
type: rule
title: 成员单位删除前置在途校验
page_key: member_remove_check_business
domain: 集团关系
status: draft
aliases:
  - 删除成员单位在途校验
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 成员单位删除前置在途校验

`removeRootGroup` 先扁平化集团树，再调额度/产品在途校验，存在在途业务时抛 `HAS_BUSINESS_PROCESS`，阻断删除。

## 需求背景

成员单位可能已有额度或产品在途，直接删除会造成业务悬空，因此删除前必须整树校验。关系结构见 [[member_unit]]、[[cust_group_rel]]。

需求文档另主张“删除权限：不支持物理删除，只支持逻辑删除（冻结/注销）”。该主张**与代码不符**：`removeRootGroup` 最终调用 `groupRelService.removeBatchByIds(collect)`，集团成员单位关系是物理删除；文档所述“冻结/注销”在当前证据中未出现对应写值点。

## 版本演进

- 当前实现为物理删除 + 前置在途校验；若后续改为逻辑删除，本规则与删除链路需同步调整。

```ground:rule
name: 成员单位删除前置在途校验
content: removeRootGroup 先扁平化集团树，再调额度/产品在途校验，有在途业务抛 HAS_BUSINESS_PROCESS
impact: 阻断删除
field_targets:
  - cust_group_rel.id
  - cust_group_rel.root_cust_id
evidence: code_path:CustGroupRelApplication.java:validateBusinessOnWay
```
---END FILE---

---FILE: rules/member_role_consistency.md ---
---
type: rule
title: 成员单位角色一致性
page_key: member_role_consistency
domain: 集团关系
status: draft
aliases:
  - 导入角色一致性校验
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
---

# 成员单位角色一致性

导入时，同一上级下所有成员单位的企业角色必须一致，且与已存在的上级企业角色一致。

## 需求背景

角色不一致会导致集团树内的权限/产品范围推导出错，因此导入阶段即拦截。角色字段与全局角色的区别见 [[enterprise_role]]。

## 版本演进

- 该校验仅在导入链路（`checkRoleExcelData`）生效，页面单个新增路径由不同校验覆盖，需注意两条入口的规则不完全对称。

```ground:rule
name: 成员单位角色一致性
content: 导入时同一上级下所有成员单位的企业角色必须一致，且与已存在上级企业角色一致
impact: 导入校验
field_targets:
  - cust_group_rel.cust_type
evidence: code_path:CustGroupRelApplication.java:checkRoleExcelData
```
---END FILE---

---FILE: rules/async_notice_tolerant.md ---
---
type: rule
title: 签署待办异步容错发送
page_key: async_notice_tolerant
domain: 集团关系
status: draft
aliases:
  - 待办异步发送
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
  - reqdoc
contract_version: "0.1"
---

# 签署待办异步容错发送

签署待办通过 `@Async("custGroupThreadPool")` 异步发送，并在事务提交后（`TransactionSynchronization.afterCommit`）触发；发送异常仅 `log.warn`，不阻断主流程。

## 需求背景

需求文档要求：“消息异步发送，不阻塞主流程；发送失败记录日志，不抛出异常。”代码实现与该主张一致：异步线程池 + 事务提交后回调 + catch 记 warn，保证集团关系落库不被通知失败回滚，见 [[cust_group_rel_status]]、[[notice_no_duplicate]]。

## 版本演进

- 需求文档另有主张“所有通知同步发送站内信，用户登录后可查看站内信”。**该主张为 document_claim，未证实**：当前证据只覆盖 `noticeProvider`/`complete` 的待办发送与消除，站内信落库链路未出现在给出的文件中。
- 由于异常被吞掉，通知失败只在日志可见，运营排查需以日志为准。

```ground:rule
name: 签署待办异步容错发送
content: '@Async 线程池 + 事务提交后 afterCommit 触发，异常仅 log.warn 不阻断主流程'
impact: 异步/容错
field_targets:
  - cust_group_rel.status
evidence: code_path:CustGroupRelApplication.java:sendCustGroupRelNotice + reqdoc:msg-async-not-block
```
---END FILE---

---REVIEW: table | scope.databases 与字段类型未在语义分析中给出 ---
语义分析仅标注证据来源为 `db`/`code`，未给出物理库名与列类型。各表页 `scope.databases` 暂填服务名派生的 `customer_management`，`ground:table` 的 `type` 一律填 `unknown`，均需回库确认后回填；确认前不要据此生成 DDL 或类型相关的对比结论。
---END REVIEW---

---REVIEW: enum | cust_account_info.auth_state 键形态与审计备注截断 ---
枚举审计中 `APPLY_10` 的 verdict 为 `reject`，证据显示写值点用 `getDictParam()`（CustAccountApplication.java:193）、查询点用 `getDictKey()`（CustAccountApplication.java:222），但审计 note 在给定材料中被截断（止于“同一枚举”）。`auth_state` 的实际落库形态、以及 APPLY_20/APPLY_30/APPLY_40 是否同样存在键混用，需回源码确认后再补 [[auth_state]] 与 [[bank_account_auth_state]]。
---END REVIEW---

---REVIEW: rule | reqdoc slug 缺失 ---
reqdoc_claims 中 action=anchor 的主张未提供 slug，[[async_notice_tolerant]] 的 `ground:rule.evidence` 暂以 `reqdoc:msg-async-not-block` 占位。需补正式的 reqdoc slug 后再定稿双源引用；action=review 的两条主张（企业状态流转、站内信落库）同理缺 slug。
---END REVIEW---