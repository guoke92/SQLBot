---FILE: tables/cust_company_info.md ---
---
type: table
title: 企业信息表
page_key: cust_company_info
domain: 企业建档与认证
status: draft
aliases:
  - 企业主数据
  - 客户企业信息表
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java
  - code_path:ApplyCompanyInfoApplication.java
  - code_path:CustCompanyOperationApplication.java
  - reqdoc:企业名称与统一社会信用代码唯一
contract_version: "0.1"
---

> (document_claim，未证实) 本页 ## 版本演进 含需求文档主张，尚未在代码中证实。

cust_company_info 是企业建档与认证主题的聚合根表。同一套表结构通过 `data_type` 区分主数据（'1'）、记录数据（'0'）与流程申请数据（'2'），因此企业主数据与每一次认证/变更产生的流程数据共存于一张表，并通过 `main_data_id` / `apply_data_id` 双向挂接。企业当前处于什么阶段由两个正交状态字段共同表达：`cust_build_status` 描述建档/认证流程主状态（见 [[processes/cust_build_status_state_machine]]），`cust_status` 描述企业生命周期状态（见 [[processes/cust_status_state_machine]]）。围绕这两条状态线，衍生出在途流程判定、生效企业口径等 [[calibers/effect_company_scope]] 一类口径，以及 [[rules/applying_record_uniqueness]] 等约束。

```ground:table
table: cust_company_info
evidence: code_path:CustCompanyInfoApplication.java:importCustCompany + reqdoc:企业名称与统一社会信用代码唯一
fields:
  - name: cust_build_status
    type: unknown
    desc: 企业建档/认证流程主状态（区分初始化、待客户认证、运营中台审批中、认证成功/失败、待激活、变更等）
    dict: ""
  - name: cust_status
    type: unknown
    desc: 企业生命周期状态（ADD 新增建档中 / EFFECT 生效 / CHANGE 变更中 / FREEZE 冻结 / WRITEOFF 注销）
    dict: ""
  - name: identify_style
    type: unknown
    desc: 认证方式：INVITE_AGW 平台录入邀请认证、INVITE 客户录入邀请认证、SELF 自主认证、SIMPLE 简易认证
    dict: ""
  - name: cust_build_type
    type: unknown
    desc: 录入方式（AGW_BUILD 运营/内管端录入，PC_BUILD 客户端录入）；与 identify_style 是不同维度，DB 中出现的 SIMPLE 属脏值
    dict: ""
  - name: check_status
    type: unknown
    desc: 运营中台审核状态：CUST_CHECK_INIT/CHECKING/PASS/BACKTOCUSTOM/REJECT（写自 OperApiConstants.CheckStatus），非 Enum 底稿中的字段
    dict: ""
  - name: ca_register_status
    type: unknown
    desc: CA(电子签章)开通状态：N 未开通 / Y 已开通 / P 开通中
    dict: ""
  - name: bs_register_status
    type: unknown
    desc: 上上签开通状态 N/Y
    dict: ""
  - name: need_register_ca
    type: unknown
    desc: 是否需要开通 CFCA 电子签章 Y/N
    dict: ""
  - name: need_register_bs
    type: unknown
    desc: 是否需要开通上上签 Y/N
    dict: ""
  - name: data_type
    type: unknown
    desc: 数据类型：'1' 主数据(main) / '0' 记录数据(record) / '2' 流程申请数据(apply)
    dict: ""
  - name: apply_type
    type: unknown
    desc: 流程类型，字面量直写 add / update
    dict: ""
  - name: main_data_id
    type: unknown
    desc: 流程数据指向的主数据 id（认证/变更流程数据回归档用）
    dict: ""
  - name: apply_data_id
    type: unknown
    desc: 主数据上挂的最近一次认证流程数据 id
    dict: ""
  - name: certification_no
    type: unknown
    desc: 统一社会信用代码
    dict: ""
  - name: cust_source
    type: unknown
    desc: 建档数据来源：PPLATFORM/PLATFORM_PUSH/MIGRATORY/PLATFORM
    dict: ""
  - name: sign_mode
    type: unknown
    desc: 签署方式；DB 实际值 ONLINE，与 SignModeEnum(01/02/03) 不一致
    dict: ""
  - name: cust_company_type
    type: unknown
    desc: 企业角色 JSON 数组字符串，如 ["SUPPLIER"]
    dict: ""
  - name: back_reason
    type: unknown
    desc: 流程退回原因
    dict: ""
  - name: pc_task_id
    type: unknown
    desc: 客户端补充资料节点的流程 taskId
    dict: ""
  - name: audit_back_flag
    type: unknown
    desc: 审核退回标记 Y/N
    dict: ""
```

## 需求背景

需求文档约定企业名称、统一社会信用代码在同一租户下唯一（anchor，双源：code_path:CustCompanyInfoApplication.java:importCustCompany + reqdoc:企业名称与统一社会信用代码唯一）。代码侧目前可见的落地只在导入录入路径——按 `certification_no` + 租户查重；企业管理员维度的同租户唯一性校验在给定链路中未全部可见。表上 `data_type`/`main_data_id`/`apply_data_id` 三件套支撑的是"流程数据回写主数据"的归档模型，见 [[rules/apply_data_archive_to_main]]。

## 版本演进

- (document_claim，未证实) 营业执照/法人身份证必传、文件类型与大小限制：未在给定链路文件中发现对应校验，需在影像/表单校验链路确认。
- (document_claim，未证实) 菜单权限过滤（code='0891344a3a4442179e98819cbe926ced' 自动过滤）：属权限/菜单模块，非本次建档主题，待归属页面。

关联页面：[[concepts/identify_style]]、[[concepts/build_success]]、[[calibers/main_data_judgment]]、[[calibers/effect_company_scope]]、[[rules/status_update_optimistic_match]]。

---REVIEW: table | 企业信息表---
- `cust_build_type`：语义为录入方式（AGW_BUILD / PC_BUILD），但 DB 中出现 `SIMPLE` 值，属脏值；`SIMPLE` 本属 identify_style（简易认证）维度，需确认历史数据来源与清理口径。
- `sign_mode`：DB 实际写值为 `ONLINE`，与 SignModeEnum(01/02/03) 不一致，需确认以写值点为准还是枚举底稿为准。
- `scope.databases` 的物理库名未在本次语义分析证据中给出，暂记 `unknown`，待补充。
---END REVIEW---

---END FILE---

---FILE: processes/cust_build_status_state_machine.md ---
---
type: process
title: 企业建档/认证状态机
page_key: cust_build_status_state_machine
domain: 企业建档与认证
status: draft
aliases:
  - 建档状态流转
  - cust_build_status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java
  - code_path:ApplyCompanyInfoApplication.java
  - code_path:CustCompanyOperationApplication.java
  - reqdoc:企业状态流转规则
  - reqdoc:自动审核
  - reqdoc:企业信息变更流程
contract_version: "0.1"
---

`cust_build_status` 描述企业从初始化到认证成功/失败的全过程主状态，落在 [[tables/cust_company_info]] 上。四条入口互不相同：邀请认证（平台录入/客户录入）、自主认证、简易认证、内管发起建档，它们分别把企业推入"待客户认证""审核中""待客户确认"等不同泳道，最终收敛到 `BUILD_SUCCESS`。与它正交的生命周期状态见 [[processes/cust_status_state_machine]]，两者在认证通过时被同一次更新同时改写（见 [[rules/apply_data_archive_to_main]]）。

```ground:process
name: 企业建档/认证状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_enum
  - value: TO_BE_BUILD
    label: 未建档
    source: code_enum
  - value: BUILDING
    label: 建档中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
    source: db_dist
  - value: BUILD_FAIL
    label: 认证失败
    source: db_dist
  - value: BUILD_BACK
    label: 退回
    source: db_dist
  - value: BUILD_ACTIVATE
    label: 待激活
    source: db_dist
  - value: CUST_CONFIRM_AWAIT
    label: 待客户认证
    source: db_dist
  - value: CUST_AUDIT_AWAIT
    label: 待审核
    source: db_dist
  - value: CUST_BUILDING
    label: 审核中/审批中
    source: db_dist
  - value: CUST_BUILD_SUCCESS
    label: 审核通过
    source: code_enum
  - value: CUST_BUILD_FAIL
    label: 审核拒绝
    source: code_enum
  - value: CUST_CHANGE
    label: 变更
    source: db_dist
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认(简易认证)
    source: db_dist
transitions:
  - from: INIT
    event: 邀请认证-客户录入提交(submitCust)
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:submitCust:getCustBuildStatus
  - from: INIT
    event: 邀请认证-平台录入提交(submitCust)
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:submitCust:getCustBuildStatus
  - from: BUILD_FAIL
    event: 自主认证重提交(INIT/BUILD_FAIL→CUST_CONFIRM_AWAIT)
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify + reqdoc:企业状态流转规则
  - from: CUST_CONFIRM_AWAIT
    event: 客户向运营中台提交
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 运营中台退回客户确认
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 运营中台审核通过
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus:after==BUILD_SUCCESS + reqdoc:企业状态流转规则
  - from: CUST_CONFIRM_AWAIT
    event: 运营中台审核拒绝
    to: BUILD_FAIL
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify:after==BUILD_FAIL
  - from: CUST_CONFIRM_AWAIT
    event: 重新认证
    to: INIT
    evidence: code_path:CustCompanyOperationApplication.java:reAuthentication
  - from: INIT
    event: 简易认证提交(非资金方)
    to: AWAIT_CUST_CONFIRM
    evidence: code_path:CustCompanyInfoApplication.java:submitForSimpleAuth
  - from: AWAIT_CUST_CONFIRM
    event: 简易认证确认/资金方直接生效
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
  - from: INIT
    event: 内管发起建档流程(addCustApplyWorkFlow: INIT+CUST_CONFIRM_AWAIT+BUILD_FAIL 允许)
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:ApplyCompanyInfoApplication.java:addCustApplyWorkFlow + reqdoc:自动审核
  - from: CUST_CONFIRM_AWAIT
    event: 企业信息变更提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:ApplyCompanyInfoApplication.java:custChangeApplyWorkFlow + reqdoc:企业信息变更流程
```

## 需求背景

需求文档描述的流转是"待提交→审核中→已通过；已驳回→待提交（修改后重新提交）"（anchor，双源：code_path:CustCompanyInfoApplication.java:messageNotify / updateCustBuildStatus + reqdoc:企业状态流转规则）：实现上与文档语义一致，只是值名为 `INIT`/`BUILD_FAIL` → `CUST_CONFIRM_AWAIT` → `CUST_BUILDING` → `BUILD_SUCCESS`，并且额外存在简易认证的 `AWAIT_CUST_CONFIRM` 分支。文档主张的"自动审核（企业信息完整、未命中风控即自动通过准入）"（anchor，双源：code_path:ApplyCompanyInfoApplication.java:addCustApplyWorkFlow:autoVerifyService.asyncAuthCheck + reqdoc:自动审核），代码实为触发 `asyncAuthCheck` 企业信息核查（异步），是核查而非放行。企业信息变更流程（anchor，双源：code_path:ApplyCompanyInfoApplication.java:custChangeApplyWorkFlow + reqdoc:企业信息变更流程）走 `apply_type=update` + `CUST_CHANGE` + `copyCustRecordData` 的流程数据路径。是否进入运营中台审核由 [[rules/self_invite_need_audit]] 决定，资金方简易认证例外见 [[rules/finance_simple_direct_effect]]。

## 版本演进

v0 初稿：依据代码写值点与全量取值分布首次固化状态与迁移，无历史版本可比对。相关口径见 [[calibers/reauthentication_allowed]]、[[calibers/is_simple_building]]；状态语义边界见 [[concepts/cust_confirm_await]]、[[concepts/cust_building]]、[[concepts/build_success]]。

---REVIEW: process | 企业建档/认证状态机---
- 枚举底稿中的 `CUST_BUILD_SUCCESS`（审核通过）DB 仅 1 条且主流程写值点均使用 `BUILD_SUCCESS`，疑似历史遗留/未使用常量；`BUILDING`（建档中）DB 仅 2 条，主流程几乎只用 `CUST_BUILDING`。二者与写值点不一致，暂以写值点 + DB 分布为准。
- 本次提供的 enum_audit 列表在中途被截断，`cust_build_status` 其余取值的 java_name/stored_as 校验未能全部覆盖，待补全底稿后复核。
---END REVIEW---

---END FILE---

---FILE: processes/cust_status_state_machine.md ---
---
type: process
title: 企业生命周期状态机
page_key: cust_status_state_machine
domain: 企业建档与认证
status: draft
aliases:
  - 企业状态流转
  - cust_status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java
  - reqdoc:已通过转已冻结或已注销
contract_version: "0.1"
---

`cust_status` 描述企业主体的生命周期，与建档/认证流程状态 [[processes/cust_build_status_state_machine]] 正交：认证通过时 `cust_build_status` 置 `BUILD_SUCCESS` 且 `cust_status` 置 `EFFECT`，此后冻结/解冻/注销只在 `EFFECT`、`FREEZE`、`WRITEOFF` 之间迁移。状态迁移集中在 `custStatusOperator`，并按 `allowStatusList` 校验前置状态；变更同时通过 `clientCustStatusSyncService` 同步业务系统，见 [[rules/cust_status_sync_third_party]]。

```ground:process
name: 企业生命周期状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增(建档中)
    source: db_dist
  - value: CHANGE
    label: 变更中
    source: db_dist
  - value: EFFECT
    label: 生效
    source: db_dist
  - value: FREEZE
    label: 冻结
    source: db_dist
  - value: WRITEOFF
    label: 注销
    source: db_dist
transitions:
  - from: EFFECT
    event: 企业冻结(freeze)
    to: FREEZE
    evidence: code_path:CustCompanyInfoApplication.java:freeze:custStatusOperator + reqdoc:已通过转已冻结或已注销
  - from: FREEZE
    event: 企业解冻(unfreeze)
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java:unfreeze:custStatusOperator
  - from: EFFECT
    event: 企业注销(diable)
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java:diable:custStatusOperator + reqdoc:已通过转已冻结或已注销
  - from: ADD
    event: 认证通过
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus:after==BUILD_SUCCESS:setCustStatus(EFFECT)
```

## 需求背景

需求文档主张"已通过 → 已冻结（违规冻结）/ 已注销（主动注销）"（anchor，双源：code_path:CustCompanyInfoApplication.java:freeze / unfreeze / diable + reqdoc:已通过转已冻结或已注销）：代码在 `custStatusOperator` 中通过 `allowStatusList` 校验，`EFFECT↔FREEZE↔WRITEOFF` 迁移成立。注销时同时冻结全部用户，冻结时同时冻结企业管理员，见 [[concepts/writeoff]]、[[concepts/freeze]]。变更中（`CHANGE`）状态的进入与退出由建档/认证状态机驱动。

## 版本演进

- v0 初稿：状态取值以 DB 全量分布为准，迁移以写值点为准。
- 相关文档主张"企业状态为已冻结或已注销时不允许变更"未证实，仅记录在 [[rules/applying_record_uniqueness]] 的版本演进中。

关联页面：[[tables/cust_company_info]]、[[calibers/effect_company_scope]]、[[concepts/writeoff]]、[[concepts/freeze]]。

---END FILE---

---FILE: calibers/judge_have_applying_record.md ---
---
type: caliber
title: 在途认证/变更流程判定
page_key: judge_have_applying_record
domain: 企业建档与认证
status: draft
aliases:
  - 在途流程判定
  - judgeHaveApplyingRecord
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
contract_version: "0.1"
---

判定某企业主数据下是否还挂着一条未结束的流程申请数据，是"禁止重复变更"闸门的输入口径。判定只看流程数据（`data_type='2'`）且排除两个终态，因此处于待客户认证、审核中、变更中等任何中间态都算在途。

```ground:caliber
name: 在途认证/变更流程判定
predicate: cust_company_info.cust_build_status NOT IN ('BUILD_SUCCESS','BUILD_FAIL') AND cust_company_info.data_type = '2' AND cust_company_info.main_data_id = ?
scope: 企业是否存在在途流程，禁止重复变更
evidence: code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
```

## 需求背景

企业信息变更必须串行：上一次认证或变更流程未结束前不得再发起，否则主数据与流程数据会互相覆盖。该口径与 [[rules/applying_record_uniqueness]] 配套使用，依赖 [[tables/cust_company_info]] 上的 `data_type`、`main_data_id`、`cust_build_status` 三字段。

## 版本演进

v0 初稿：口径首次固化，无历史版本。限定条件（`data_type='2'` + `main_data_id` 绑定）是否对全部入口生效，待与发起链路复核。

关联：[[calibers/main_data_judgment]]、[[processes/cust_build_status_state_machine]]。

---END FILE---

---FILE: calibers/main_data_judgment.md ---
---
type: caliber
title: 主数据判定
page_key: main_data_judgment
domain: 企业建档与认证
status: draft
aliases:
  - 主数据口径
  - data_type 主数据
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
contract_version: "0.1"
---

[[tables/cust_company_info]] 同表承载主数据（'1'）、记录数据（'0'）与流程申请数据（'2'）。凡是对"企业本身"的状态变更与生效企业查询，都必须先限定为主数据，否则会把流程数据的中间态误当作企业状态。

```ground:caliber
name: 主数据判定
predicate: cust_company_info.data_type = '1'
scope: 状态变更/生效企业查询均限定主数据
evidence: code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
```

## 需求背景

状态回写（`updateCustBuildStatus`）与生效企业清单（[[calibers/effect_company_scope]]）都建立在主数据口径之上；离开该口径，`cust_status` 的 `EFFECT` 与 `cust_build_status` 的 `BUILD_SUCCESS` 会失去唯一指向。

## 版本演进

v0 初稿：口径固化自写值点 `data_type='1'`，与 DB 中 '0'/'2' 的取值分布一致。

关联：[[calibers/judge_have_applying_record]]、[[rules/status_update_optimistic_match]]、[[rules/apply_data_archive_to_main]]。

---END FILE---

---FILE: calibers/effect_company_scope.md ---
---
type: caliber
title: 生效企业口径
page_key: effect_company_scope
domain: 企业建档与认证
status: draft
aliases:
  - 生效企业
  - getTenantCodesWithEffectCompany
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany
contract_version: "0.1"
---

用于产出"拥有至少一家生效企业"的租户集合。四个条件同时成立才算生效：流程状态认证成功、生命周期生效、是主数据、且企业启用。

```ground:caliber
name: 生效企业口径
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1' AND cust_company_info.enable = 'Y'
scope: 有生效企业的租户集合
evidence: code_path:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany
```

## 需求背景

该清单是下游能力（如门户/推送/权限）判断"租户是否已真正开业"的输入，因此必须同时约束流程状态与生命周期状态，不能只看 [[concepts/build_success]] 其中一个字段。

## 版本演进

v0 初稿：口径固化自写值点条件，无历史版本。注意与影像批处理的宽口径 [[calibers/build_success_company_scope]] 不同——后者不校验 `cust_status`。

关联：[[tables/cust_company_info]]、[[processes/cust_status_state_machine]]、[[calibers/main_data_judgment]]。

---END FILE---

---FILE: calibers/build_success_company_scope.md ---
---
type: caliber
title: 建档成功企业口径(影像批处理)
page_key: build_success_company_scope
domain: 企业建档与认证
status: draft
aliases:
  - 建档成功企业
  - getAllBuildSuccessCompanies
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CompanyImageUpdateJobHandler.java:getAllBuildSuccessCompanies
contract_version: "0.1"
---

影像更新批处理的扫描范围口径：只要流程状态为认证成功且企业启用即纳入，不区分生命周期状态，也不强求主数据标识。相比 [[calibers/effect_company_scope]] 更宽，用于保证已认证企业的影像被持续补齐。

```ground:caliber
name: 建档成功企业口径(影像批处理)
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.enable = 'Y'
scope: CompanyImageUpdateJobHandler 扫描范围
evidence: code_path:CompanyImageUpdateJobHandler.java:getAllBuildSuccessCompanies
```

## 需求背景

批处理需要在冻结、变更中等状态下仍能扫描到已认证企业，因此刻意不放 `cust_status` 条件；这也意味着它不能被复用作"生效企业"判断。

## 版本演进

v0 初稿：口径固化自批处理写值点。与生效企业口径的差异已显式记录，供后续判断是否为有意的宽口径。

关联：[[calibers/effect_company_scope]]、[[tables/cust_company_info]]。

---END FILE---

---FILE: calibers/reauthentication_allowed.md ---
---
type: caliber
title: 待客户确认可重新认证
page_key: reauthentication_allowed
domain: 企业建档与认证
status: draft
aliases:
  - 允许重新认证
  - reAuthentication
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyOperationApplication.java:reAuthentication
contract_version: "0.1"
---

"重新认证"动作的准入口径：只有当前处于待客户认证（`CUST_CONFIRM_AWAIT`）的企业，才允许被重置回 `INIT` 重走一遍认证流程。它是 [[processes/cust_build_status_state_machine]] 中 `CUST_CONFIRM_AWAIT → INIT` 这条回边的守卫条件。

```ground:caliber
name: 待客户确认可重新认证
predicate: cust_company_info.cust_build_status = 'CUST_CONFIRM_AWAIT'
scope: 仅该状态允许 reAuthentication
evidence: code_path:CustCompanyOperationApplication.java:reAuthentication
```

## 需求背景

客户长时间未完成确认时，运营需要能主动把流程打回起点重新发起，而不必新建一条企业记录；限制在单一前置状态是为了避免打断已在运营中台审核中的流程。

## 版本演进

v0 初稿：口径固化自 `reAuthentication` 的校验。是否为唯一入口（存在其他重置路径）待复核。

关联：[[concepts/cust_confirm_await]]、[[calibers/judge_have_applying_record]]。

---END FILE---

---FILE: calibers/is_simple_building.md ---
---
type: caliber
title: 简易认证在建档中判定
page_key: is_simple_building
domain: 企业建档与认证
status: draft
aliases:
  - 简易建档流程中
  - isSimpleBuilding
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyUtilApplication.java:isSimpleBuilding
contract_version: "0.1"
---

判断企业是否正处在简易认证的建档过程中：必须认证方式为简易，且未落到变更态与认证成功态。两个排除条件实际上是"未走到终态"的近似表达。

```ground:caliber
name: 简易认证在建档中判定
predicate: cust_company_info.identify_style = 'SIMPLE' AND cust_company_info.cust_build_status != 'CUST_CHANGE' AND cust_company_info.cust_build_status != 'BUILD_SUCCESS'
scope: 简易建档流程中
evidence: code_path:CustCompanyUtilApplication.java:isSimpleBuilding
```

## 需求背景

简易认证与邀请/自主认证走不同链路（见 [[rules/simple_auth_no_ca]]、[[rules/finance_simple_direct_effect]]），下游需要据此区分企业是否还在简易建档中，从而决定是否允许触发相关动作。

## 版本演进

v0 初稿：口径固化自 `isSimpleBuilding`。用 `!=` 排除两个状态而非枚举在途状态，是否遗漏 `BUILD_FAIL` 等取值需复核。

关联：[[concepts/identify_style]]、[[processes/cust_build_status_state_machine]]。

---END FILE---

---FILE: calibers/need_register_ca_and_not_open.md ---
---
type: caliber
title: 需开通CA且未开通
page_key: need_register_ca_not_open
domain: 企业建档与认证
status: draft
aliases:
  - 待签 CFCA 协议
  - selectCustNeedSingCfca
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:selectCustNeedSingCfca
contract_version: "0.1"
---

筛出"业务上需要开通电子签章、但当前尚未开通"的企业，用于判断客户是否还需签署 CFCA 协议。两个条件必须同时成立：需求标记为 Y，开通状态为 N（`P` 开通中不算）。

```ground:caliber
name: 需开通CA且未开通
predicate: cust_company_info.need_register_ca = 'Y' AND cust_company_info.ca_register_status = 'N'
scope: 判断客户是否需签署 CFCA 协议
evidence: code_path:ApplyCompanyInfoApplication.java:selectCustNeedSingCfca
```

## 需求背景

电子签章开通是认证链路的后续动作，简易认证被强制不开通 CA（见 [[rules/simple_auth_no_ca]]），因此该口径与 [[tables/cust_company_info]] 上的 `need_register_ca` / `ca_register_status` 写值点强耦合。上上签侧有对称字段 `need_register_bs` / `bs_register_status`。

## 版本演进

v0 初稿：口径固化自 `selectCustNeedSingCfca`。`ca_register_status='P'`（开通中）被排除的合理性待确认。

关联：[[concepts/identify_style]]、[[rules/simple_auth_no_ca]]。

---END FILE---

---FILE: concepts/identify_style.md ---
---
type: concept
title: 认证方式
page_key: identify_style
domain: 企业建档与认证
status: draft
aliases:
  - identify_style
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java
  - code_path:ApplyCompanyInfoApplication.java
contract_version: "0.1"
maps_to: cust_company_info.identify_style
field_targets:
  - cust_company_info.identify_style
  - cust_company_info.cust_build_type
adjudication: boundary
also_confused_with:
  - cust_company_info.cust_build_type
---

> (document_claim，未证实) 本页 ## 版本演进 含需求文档主张，尚未在代码中证实。

"认证方式"指企业以哪条路径完成认证：`INVITE_AGW`（平台录入邀请认证）、`INVITE`（客户录入邀请认证）、`SELF`（自主认证）、`SIMPLE`（简易认证）。它决定提交后进入哪条泳道、是否需要运营中台审核，见 [[rules/self_invite_need_audit]]、[[rules/finance_simple_direct_effect]]。

## 边界与歧义

与 `cust_build_type` 的边界：`identify_style` 表示认证路径（INVITE/INVITE_AGW/SELF/SIMPLE），`cust_build_type` 表示录入端（AGW_BUILD 运营/内管端、PC_BUILD 客户端）。两者是独立维度，不可互相代替或混用；DB 中 `cust_build_type` 出现 `SIMPLE` 属脏值，见 [[tables/cust_company_info]] 的 REVIEW。

## 需求背景

邀请/自主认证需经运营中台审核，简易认证无需审批，这一差异完全由本字段驱动，因此字段取值一旦写错，会影响整条审批链路。

## 版本演进

- (document_claim，未证实) 用户邀请与注册流程（邀请码 8 位 30 天有效、邮件异步、SSO/AMS 同步）：未在给定链路文件中发现实现，涉及 UserFacade/EmailAsyncService，属另一模块，与本页 INVITE 认证方式的入口相关但尚未证实。

关联：[[processes/cust_build_status_state_machine]]、[[calibers/is_simple_building]]、[[calibers/need_register_ca_not_open]]。

---END FILE---

---FILE: concepts/build_success.md ---
---
type: concept
title: 建档成功 / 认证成功
page_key: build_success
domain: 企业建档与认证
status: draft
aliases:
  - BUILD_SUCCESS
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
field_targets:
  - cust_company_info.cust_build_status
  - cust_build_status.BUILD_SUCCESS
  - cust_company_info.cust_status
adjudication: synonym
also_confused_with:
  - cust_build_status.CUST_BUILD_SUCCESS
  - cust_company_info.cust_status = 'EFFECT'
---

业务口径中的"认证成功"在代码中即 `cust_build_status = 'BUILD_SUCCESS'`，且同一次更新会把生命周期状态记为 `EFFECT`。它是多条口径的锚点：[[calibers/effect_company_scope]]、[[calibers/build_success_company_scope]] 都以它为前提。

## 边界与歧义

- 与 `CUST_BUILD_SUCCESS` 的边界：后者是枚举中另一个声明值（"审核通过"），DB 仅 1 条，主流程所有写值点均使用 `BUILD_SUCCESS`，疑为历史遗留常量。
- 与 `cust_status = 'EFFECT'` 的边界：二者在认证通过时同点写入，但语义不同——前者是流程状态，后者是生命周期状态，查询时不可互相替代。

## 需求背景

需求文档中的"已通过"对应本概念；下游"是否有生效企业"的判断需要流程状态与生命周期状态同时成立，见 [[calibers/effect_company_scope]]。

## 版本演进

v0 初稿：以写值点 + DB 分布为准固化；`CUST_BUILD_SUCCESS` 的一致性疑点记录在 [[processes/cust_build_status_state_machine]] 的 REVIEW 中。

关联：[[processes/cust_build_status_state_machine]]、[[rules/apply_data_archive_to_main]]。

---END FILE---

---FILE: concepts/cust_confirm_await.md ---
---
type: concept
title: 待客户认证
page_key: cust_confirm_await
domain: 企业建档与认证
status: draft
aliases:
  - CUST_CONFIRM_AWAIT
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:submitCust
  - code_path:CustCompanyOperationApplication.java:reAuthentication
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
field_targets:
  - cust_company_info.cust_build_status
  - cust_build_status.CUST_CONFIRM_AWAIT
  - cust_build_status.AWAIT_CUST_CONFIRM
adjudication: boundary
also_confused_with:
  - cust_build_status.AWAIT_CUST_CONFIRM
---

"待客户认证"指流程已发起但球在企业一侧：邀请认证的客户录入提交、自主认证的重提交、内管发起建档都会落到该状态，等待客户向运营中台提交后才进入审核中。它是 [[calibers/reauthentication_allowed]] 的唯一准入态。

## 边界与歧义

与 `AWAIT_CUST_CONFIRM` 的边界：两值字面近似但语义不同——`CUST_CONFIRM_AWAIT` 是邀请/自主认证的"待客户确认"；`AWAIT_CUST_CONFIRM` 由简易认证提交写入（`submitForSimpleAuth`），走的是另一条无需运营中台审批的链路，见 [[processes/cust_build_status_state_machine]]。

## 需求背景

需求文档中"待提交"态在本字段落地为该值；"已驳回→待提交（修改后重新提交）"即从 `BUILD_FAIL` 回到本状态。

## 版本演进

v0 初稿：取值以 DB 分布为准。两值是否应合并或改名，待产品与研发确认。

关联：[[concepts/cust_building]]、[[rules/self_invite_need_audit]]、[[calibers/reauthentication_allowed]]。

---END FILE---

---FILE: concepts/cust_building.md ---
---
type: concept
title: 审批中/审核中
page_key: cust_building
domain: 企业建档与认证
status: draft
aliases:
  - CUST_BUILDING
  - BUILDING
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:messageNotify
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
field_targets:
  - cust_company_info.cust_build_status
  - cust_build_status.CUST_BUILDING
  - cust_build_status.BUILDING
adjudication: boundary
also_confused_with:
  - cust_build_status.BUILDING
---

"审核中/审批中"指流程已提交运营中台、等待审批的状态，是认证成功前的最后一个中间态：客户提交后由 `CUST_CONFIRM_AWAIT` 进入，运营中台退回则回退，通过则进入 [[concepts/build_success]]。

## 边界与歧义

与 `BUILDING` 的边界：`CUST_BUILDING` 是提交运营中台后的真实审核态（DB 2909 条）；`BUILDING` 在枚举中意为"建档中"，DB 仅 2 条，主流程基本不使用。两者不可等同。

## 需求背景

需求文档中的"审核中"对应本概念；变更流程中的企业也可能以 `cust_build_status = 'CUST_CHANGE'` 等方式并行表达，需与 [[concepts/cust_confirm_await]] 区分。

## 版本演进

v0 初稿：以 DB 分布为准确认主用值；`BUILDING` 的存量数据归属待清理确认。

关联：[[processes/cust_build_status_state_machine]]、[[calibers/judge_have_applying_record]]。

---END FILE---

---FILE: concepts/writeoff.md ---
---
type: concept
title: 注销
page_key: writeoff
domain: 企业建档与认证
status: draft
aliases:
  - WRITEOFF
  - DISABLE
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:diable
contract_version: "0.1"
maps_to: cust_company_info.cust_status
field_targets:
  - cust_company_info.cust_status
  - cust_status.WRITEOFF
  - cust_company_info.enable
adjudication: synonym
also_confused_with:
  - cust_company_info.enable
---

"注销"是生命周期终态：调用 `diable()` 把 `cust_status` 置为 `WRITEOFF`，并同时冻结该企业下的全部用户。业务叙述中的"主动注销"即此动作。

## 边界与歧义

与 `enable` 字段的边界：`enable` 表达企业是否启用，与 `cust_status='WRITEOFF'` 不是同一维度；不要把 `enable='N'` 读作注销。

## 需求背景

需求文档主张"已通过 → 已注销"（anchor，双源：code_path:CustCompanyInfoApplication.java:diable:custStatusOperator + reqdoc:已通过转已冻结或已注销），并伴随用户冻结。注销后是否仍允许变更，见 [[rules/applying_record_uniqueness]] 中的未证实主张。

## 版本演进

v0 初稿：以 `custStatusOperator` 的 `allowStatusList` 校验与写值点为准。

关联：[[concepts/freeze]]、[[processes/cust_status_state_machine]]、[[rules/cust_status_sync_third_party]]。

---END FILE---

---FILE: concepts/freeze.md ---
---
type: concept
title: 冻结
page_key: freeze
domain: 企业建档与认证
status: draft
aliases:
  - FREEZE
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:freeze
  - code_path:CustCompanyInfoApplication.java:unfreeze
contract_version: "0.1"
maps_to: cust_company_info.cust_status
field_targets:
  - cust_company_info.cust_status
  - cust_status.FREEZE
adjudication: synonym
also_confused_with: []
---

"冻结"表示企业主体被暂停使用：`cust_status` 由 `EFFECT` 置为 `FREEZE`，解冻则由 `FREEZE` 回到 `EFFECT`。冻结企业时会同时冻结企业管理员，且状态变更会同步业务系统，见 [[rules/cust_status_sync_third_party]]。

## 边界与歧义

业务叙述中的"违规冻结"即此动作；与注销的区别在于可逆——解冻后企业回到生效态，而 [[concepts/writeoff]] 不可逆。

## 需求背景

需求文档主张"已通过 → 已冻结"（anchor，双源：code_path:CustCompanyInfoApplication.java:freeze:custStatusOperator + reqdoc:已通过转已冻结或已注销），代码在 `custStatusOperator` 中以 `allowStatusList` 校验前置状态。

## 版本演进

v0 初稿：以冻结/解冻写值点为准。冻结是否影响在途流程的处理，待复核。

关联：[[concepts/writeoff]]、[[processes/cust_status_state_machine]]、[[calibers/effect_company_scope]]。

---END FILE---

---FILE: rules/applying_record_uniqueness.md ---
---
type: rule
title: 在途流程唯一性
page_key: applying_record_uniqueness
domain: 企业建档与认证
status: draft
aliases:
  - 禁止重复变更
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
  - reqdoc:企业状态为已冻结或已注销时不允许变更
contract_version: "0.1"
---

> (document_claim，未证实) 本页 ## 版本演进 含需求文档主张，尚未在代码中证实。

同一企业主数据下同时只允许存在一条在途流程：若还挂着未结束的申请数据（状态非 `BUILD_SUCCESS`/`BUILD_FAIL`），再次发起变更会被拒绝。判定依据见 [[calibers/judge_have_applying_record]]。

```ground:rule
name: 在途流程唯一性
content: 同一企业主数据存在未结束的 apply 数据(状态非 BUILD_SUCCESS/BUILD_FAIL)时禁止再次发起变更
impact: 重复变更被拒
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.data_type
  - cust_company_info.main_data_id
evidence: code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
```

## 需求背景

变更流程会改写主数据，若允许并行发起，两次流程的归档回写会互相覆盖（见 [[rules/apply_data_archive_to_main]]）。因此需要在发起前做在途判定，把并发收敛为串行。

## 版本演进

- v0 初稿：规则以 `judgeHaveApplyingRecord` 的实现固化。
- (document_claim，未证实) 需求文档主张"企业状态为已冻结或已注销时不允许变更"：代码侧对应校验位于 `custStatusOperator` 的 `config.getNeedCheckInWay()` 分支，该分支当前为 TODO 空实现，限制并未真正落地，需在开关实装后复核。

关联：[[processes/cust_build_status_state_machine]]、[[concepts/freeze]]、[[concepts/writeoff]]。

---REVIEW: rule | 在途流程唯一性---
- 在途校验开关 `needCheckInWay` 分支为空实现（TODO），无法确认冻结/注销企业的变更限制是否已生效；当前仅能确认"未结束流程即拒绝"这一路径。
---END REVIEW---

---END FILE---

---FILE: rules/status_update_optimistic_match.md ---
---
type: rule
title: 状态更新乐观匹配
page_key: status_update_optimistic_match
domain: 企业建档与认证
status: draft
aliases:
  - 状态更新前置条件
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
---

更新 `cust_build_status` 时，写条件要求 before 状态、`enable='Y'`、主数据标识同时匹配；任一不满足则更新 0 行，状态不会被覆盖。

```ground:rule
name: 状态更新乐观匹配
content: 更新 cust_build_status 时要求 before 状态、enable=Y、data_type=主数据同时匹配，否则更新 0 行
impact: 并发/脏数据下状态不被覆盖
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.enable
  - cust_company_info.data_type
evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
```

## 需求背景

状态机迁移由消息回调与运营中台审核共同驱动，存在并发与重复投递的可能。以"期望前置状态"作为更新条件，可以保证迁移只在合法起点上发生，也让 [[processes/cust_build_status_state_machine]] 的迁移表具有可验证性。

## 版本演进

v0 初稿：以 `updateCustBuildStatus` 的实现固化。更新 0 行时的补偿/告警策略未在给定证据中体现。

关联：[[calibers/main_data_judgment]]、[[processes/cust_build_status_state_machine]]。

---END FILE---

---FILE: rules/simple_auth_no_ca.md ---
---
type: rule
title: 简易建档不支持电子签章
page_key: simple_auth_no_ca
domain: 企业建档与认证
status: draft
aliases:
  - 简易认证强制不开通 CA
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:submitForSimpleAuth
contract_version: "0.1"
---

简易认证提交时，即使请求中 `need_register_ca='Y'`，也会被强制校正为不开通，并落库 CA/上上签相关字段，保证简易链路不进入签章开通流程。

```ground:rule
name: 简易建档不支持电子签章
content: 简易认证提交时若 need_register_ca=Y，强制校正为不开通并落库 CA/BS 字段
impact: 简易建档不会走 CA 开通链路
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.need_register_bs
  - cust_company_info.bs_register_status
evidence: code_path:CustCompanyInfoApplication.java:submitForSimpleAuth:CustCompanyCaPolicy.enforceMustNotOpenCa
```

## 需求背景

简易认证面向轻量场景，不要求电子签章，因此需要在提交入口统一裁剪签章诉求，避免下游按 [[calibers/need_register_ca_not_open]] 误判为待签 CFCA 协议。

## 版本演进

v0 初稿：规则以 `CustCompanyCaPolicy.enforceMustNotOpenCa` 的实现固化。

关联：[[concepts/identify_style]]、[[rules/finance_simple_direct_effect]]、[[calibers/is_simple_building]]。

---END FILE---

---FILE: rules/self_invite_need_audit.md ---
---
type: rule
title: 自主/邀请认证需运营中台审核
page_key: self_invite_need_audit
domain: 企业建档与认证
status: draft
aliases:
  - 认证需运营中台审批
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:submitCust
contract_version: "0.1"
---

认证方式为 `SELF`/`INVITE`/`INVITE_AGW` 时，提交后进入 `CUST_CONFIRM_AWAIT` 或 `CUST_BUILDING` 并推送运营中台审核；只有简易认证路径无需审批。该规则决定是否发起运营中台审批。

```ground:rule
name: 自主/邀请认证需运营中台审核
content: identify_style=SELF/INVITE/INVITE_AGW 提交后进入 CUST_CONFIRM_AWAIT/CUST_BUILDING 并推送运营中台审核；仅简易认证无需审批
impact: 决定是否发起运营中台审批
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.identify_style
evidence: code_path:CustCompanyInfoApplication.java:submitCust
```

## 需求背景

认证方式区分了"客户自证"与"平台轻量录入"两类场景（见 [[concepts/identify_style]]），邀请/自主路径需要运营中台把关（对应审核状态字段 `check_status`），简易路径则以客户确认为准。审批状态推进见 [[processes/cust_build_status_state_machine]]。

## 版本演进

v0 初稿：规则以 `submitCust` 的分支写值点固化。运营中台侧回推消息的处理见 `messageNotify`。

关联：[[concepts/cust_building]]、[[concepts/cust_confirm_await]]、[[rules/finance_simple_direct_effect]]。

---END FILE---

---FILE: rules/finance_simple_direct_effect.md ---
---
type: rule
title: 资金方简易认证直接生效
page_key: finance_simple_direct_effect
domain: 企业建档与认证
status: draft
aliases:
  - 资金方零审批建档
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:submitForSimpleAuth
contract_version: "0.1"
---

简易认证路径下的例外：当企业类型为 `FINANCE`（资金方）时，提交即置为 `BUILD_SUCCESS` 且生命周期置 `EFFECT`，不等待客户确认，形成零审批落库。

```ground:rule
name: 资金方简易认证直接生效
content: 简易认证且企业类型为 FINANCE 时，提交即置 BUILD_SUCCESS + cust_status=EFFECT，不待确认
impact: 资金方建档零审批落库
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.cust_status
  - cust_company_info.cust_company_type
evidence: code_path:CustCompanyInfoApplication.java:submitForSimpleAuth
```

## 需求背景

资金方企业由平台侧确认，无需再走客户确认环节（对比 [[concepts/cust_confirm_await]] 的 `AWAIT_CUST_CONFIRM` 分支）。企业类型以 `cust_company_type` 的 JSON 数组形式表达，见 [[tables/cust_company_info]]。

## 版本演进

v0 初稿：规则以 `submitForSimpleAuth` 的分支写值点固化。`cust_company_type` 中多角色并存时的判定顺序待复核。

关联：[[rules/simple_auth_no_ca]]、[[concepts/build_success]]、[[calibers/effect_company_scope]]。

---END FILE---

---FILE: rules/apply_data_archive_to_main.md ---
---
type: rule
title: 流程数据归档回主数据
page_key: apply_data_archive_to_main
domain: 企业建档与认证
status: draft
aliases:
  - 认证成功回写主数据
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:setApplyDataToMain
contract_version: "0.1"
---

认证成功后，流程申请数据（`data_type='2'`）的内容被回写到主数据（`data_type='1'`）：企业、人员、账户、关联方、开通产品、影像均按此复制，并在主数据上回写 `apply_data_id` 以记录最近一次认证流程。

```ground:rule
name: 流程数据归档回主数据
content: 认证成功后 APPLY 数据回写 MAIN（copy 企业/人员/账户/关联方/开通产品/影像），并回写 apply_data_id
impact: 主数据与流程数据一致性
field_targets:
  - cust_company_info.data_type
  - cust_company_info.main_data_id
  - cust_company_info.apply_data_id
evidence: code_path:ApplyCompanyInfoApplication.java:setApplyDataToMain
```

## 需求背景

[[tables/cust_company_info]] 单表承载主数据与流程数据，认证过程中所有修改都落在流程数据上，只有认证通过才整体归档到主数据，从而保证未通过的修改不污染企业当前态。这也是 [[rules/applying_record_uniqueness]] 需要串行的原因。

## 版本演进

v0 初稿：规则以 `setApplyDataToMain` 的复制范围固化，覆盖的资源清单以代码为准。

关联：[[processes/cust_build_status_state_machine]]、[[calibers/main_data_judgment]]、[[concepts/build_success]]。

---END FILE---

---FILE: rules/cust_status_sync_third_party.md ---
---
type: rule
title: 状态同步第三方
page_key: cust_status_sync_third_party
domain: 企业建档与认证
status: draft
aliases:
  - 客户状态同步
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:custStatusSync
contract_version: "0.1"
---

企业生命周期状态变更（冻结→`FREEZE`、解冻→`EFFECT`、注销→`WRITEOFF`）通过 `clientCustStatusSyncService` 同步到业务系统；用户状态的同步则直接透传 `operateType`。

```ground:rule
name: 状态同步第三方
content: 客户状态变更(冻结→FREEZE、解冻→EFFECT、注销→WRITEOFF)通过 clientCustStatusSyncService 同步业务系统；用户状态同步 operateType 直传
impact: 跨系统状态一致性
field_targets:
  - cust_company_info.cust_status
evidence: code_path:CustCompanyInfoApplication.java:custStatusSync
```

## 需求背景

冻结与注销会影响下游系统的业务资格，因此状态迁移必须同步出去；同步点与 [[processes/cust_status_state_machine]] 的迁移同源，见 [[concepts/freeze]]、[[concepts/writeoff]]。

## 版本演进

v0 初稿：规则以 `custStatusSync` 的调用路径固化。同步失败的重试/补偿策略未在给定证据中体现。

关联：[[processes/cust_status_state_machine]]、[[concepts/writeoff]]。

---END FILE---