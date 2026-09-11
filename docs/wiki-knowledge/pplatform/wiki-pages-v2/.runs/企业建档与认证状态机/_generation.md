---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info 企业建档与认证主表
page_key: cust_company_info
domain: 企业建档与认证
status: draft
aliases:
  - cust_company_info
  - 企业客户信息表
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info
contract_version: "0.1"
---

`cust_company_info` 是企业建档与认证域的核心物理表，承载企业客户从录入、认证、审核到生效、变更、冻结、注销的全过程数据。表内并存三条彼此独立的状态主线：**认证状态**（`cust_build_status`，见 [[auth_status]] 与 [[enterprise_auth_status_machine]]）、**客户状态**（`cust_status`，见 [[customer_status]] 与 [[customer_status_machine]]）、**审核状态**（`check_status`，见 [[check_status]] 与 [[operation_check_status_machine]]）。三者常被混用，其边界已在对应 concept 页中裁定。

表还通过 `data_type` 区分同一张表内承载的三类数据：主数据、记录（暂存/变更过程）数据、申请（认证流程）数据，对应口径 [[main_data]] 与 [[process_apply_data]]。数据来源与录入途径分别由 `cust_source`、[[identify_style]]（认证方式）、[[build_type]]（录入方式）刻画；企业角色维度由 [[company_type]]（`cust_company_type`）以 JSON 数组字符串承载。审批过程信息由 `act_procinst_status`、`audit_back_flag`、`back_reason` 记录；电子签章相关字段由 `ca_register_status`/`need_register_ca` 与 `bs_register_status`/`need_register_bs` 两组承载。

```ground:table
table: cust_company_info
fields:
  - field: cust_build_status
    meaning: 企业建档/认证状态，表示企业从初始化到认证成功/失败的全流程状态
    evidence: db
  - field: cust_status
    meaning: 客户生命周期状态，表示企业生效、冻结、注销等经营状态
    evidence: db
  - field: identify_style
    meaning: 认证方式，取值如 INVITE（邀请认证-客户录入）、INVITE_AGW（邀请认证-平台录入）、SELF（自主认证）、SIMPLE（简易认证）
    evidence: db
  - field: cust_build_type
    meaning: 录入方式，取值如 AGW_BUILD（平台录入）、PC_BUILD（客户端录入）、SIMPLE（简易录入）
    evidence: db
  - field: check_status
    meaning: 运营中台审核状态，取值如 CUST_CHECK_INIT、CUST_CHECK_CHECKING、CUST_CHECK_PASS、CUST_CHECK_REJECT、CUST_CHECK_BACKTOCUSTOM、EFFECT
    evidence: db
  - field: data_type
    meaning: 数据类型：1-主数据，0-记录数据（暂存/变更过程数据），2-申请数据（认证流程数据）
    evidence: code
  - field: apply_type
    meaning: 流程类型：add-新增建档流程，update-变更流程
    evidence: code
  - field: cust_source
    meaning: 建档数据来源，取值如 MIGRATORY（迁移）、PLATFORM、PLATFORM_PUSH、PPLATFORM
    evidence: db
  - field: cust_company_type
    meaning: 企业角色，JSON数组字符串，如 ["SUPPLIER"]、["CORE"] 等
    evidence: db
  - field: act_procinst_status
    meaning: 流程实例当前审批状态，取值如 待客户确认、审批中、认证失败、退回、变更成功
    evidence: db
  - field: audit_back_flag
    meaning: 审核退回标记，Y/N
    evidence: db
  - field: back_reason
    meaning: 退回原因
    evidence: db
  - field: main_data_id
    meaning: 主数据ID，记录/申请数据指向所属主数据
    evidence: code
  - field: apply_data_id
    meaning: 认证流程数据ID，主数据指向最近一次流程数据
    evidence: db
  - field: ca_register_status
    meaning: CA开通状态，N-未开通，Y-已开通，P-开通中
    evidence: db
  - field: need_register_ca
    meaning: 是否需要开通电子签章（CA），Y/N
    evidence: db
  - field: bs_register_status
    meaning: 上上签开通状态，N-未开通，Y-已开通
    evidence: db
  - field: need_register_bs
    meaning: 是否需要开通上上签，Y/N
    evidence: db
  - field: enable
    meaning: 数据启用状态，Y-启用，N-停用
    evidence: db
```

## 需求背景

本页暂无需求文档主张可引用（语义分析中 `reqdoc_claims` 为空），以下背景完全来自数据库与代码语义分析：企业客户需要经过“录入 → 认证/审核 → 生效”的流程才能进入可经营状态，且录入途径（平台录入、客户端录入、简易录入）、认证方式（邀请认证、自主认证、简易认证）多样；同时变更、冻结、注销等经营动作也需要在同一实体上留痕。因此单表内以 `data_type` 区分主数据与过程数据，以 `main_data_id`/`apply_data_id` 建立两者关联，并以多条状态字段分别表达不同维度的进度。

## 版本演进

- v0.1：依据语义分析首次建立该表页，登记 19 个字段语义与证据来源，未引入任何需求文档主张。

---END FILE---

---FILE: processes/enterprise_auth_status_machine.md ---
---
type: process
title: 企业认证状态机（cust_build_status）
page_key: enterprise_auth_status_machine
domain: 企业建档与认证
status: draft
aliases:
  - 建档状态机
  - 认证状态流转
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:submitCust
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
  - code:ApplyCompanyInfoApplication.java:addCustApplyWorkFlow
  - code:CustCompanyOperationApplication.java:reAuthentication
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
---

本流程描述 `cust_company_info.cust_build_status`（见 [[auth_status]]）在企业建档与认证过程中的流转。该字段是**建档/认证的整体进度**，与客户生命周期状态（[[customer_status_machine]]）、运营中台单次审核状态（[[operation_check_status_machine]]）相互独立，边界见 [[customer_status]] 与 [[check_status]] 的裁定说明。

主干路径为：初始化 → 待客户确认 → 认证中 → 认证成功；分支包括认证失败后重新提交、运营退回后回到待客户确认、以及待客户确认状态下直接重置为 INIT 重新认证（受 [[reauthentication_restriction]] 约束）。平台录入（认证方式 `INVITE_AGW`）的提交会跳过“待客户确认”直接进入认证中，该差异由 [[identify_style]] 决定。认证成功是进入生效企业的必要条件之一，口径见 [[effective_company]]；相关的“认证中”“待客户确认”判断口径见 [[certifying]] 与 [[pending_customer_confirm]]。

状态更新存在并发保护约束，见 [[auth_status_conditional_update]]；认证成功会联动客户状态，见 [[auth_success_sets_customer_effective]]。

```ground:process
name: 企业认证状态机
field: cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 认证中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
    source: code_enum
  - value: BUILD_FAIL
    label: 认证失败
    source: code_enum
  - value: BUILD_BACK
    label: 退回
    source: code_enum
  - value: BUILD_ACTIVATE
    label: 待激活
    source: code_enum
  - value: CUST_CHANGE
    label: 变更中
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证）
    source: code_enum
  - value: CUST_AUDIT_AWAIT
    label: 审核等待
    source: db_dist
  - value: BUILDING
    label: 建档中
    source: db_dist
  - value: CUST_BUILD_SUCCESS
    label: 认证成功（历史值）
    source: db_dist
transitions:
  - from: INIT
    event: 提交建档（认证方式=INVITE或SELF）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:submitCust"
  - from: INIT
    event: 提交建档（认证方式=INVITE_AGW）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:submitCust"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CONFIRM_AWAIT
    event: 简易认证确认
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth"
  - from: BUILD_FAIL
    event: 重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:ApplyCompanyInfoApplication.java:addCustApplyWorkFlow"
  - from: CUST_CONFIRM_AWAIT
    event: 重新认证
    to: INIT
    evidence: "code_path:CustCompanyOperationApplication.java:reAuthentication"
```

## 需求背景

暂无需求文档主张。状态集合中 `CUST_AUDIT_AWAIT`、`BUILDING`、`CUST_BUILD_SUCCESS` 三个取值来源于数据库分布（`db_dist`）而非代码枚举，其中 `CUST_BUILD_SUCCESS` 被标注为历史值，说明该状态存在历史数据兼容问题，详见页末 REVIEW 说明。

## 版本演进

- v0.1：依据语义分析建立状态机页，登记 12 个状态（9 个代码枚举值 + 3 个数据库分布值）与 8 条流转及其代码证据。

---END FILE---

---FILE: processes/customer_status_machine.md ---
---
type: process
title: 客户状态机（cust_status）
page_key: customer_status_machine
domain: 企业建档与认证
status: draft
aliases:
  - 客户生命周期状态机
  - 生效冻结注销流转
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:freeze
  - code:CustCompanyInfoApplication.java:unfreeze
  - code:CustCompanyInfoApplication.java:diable
  - db:cust_company_info.cust_status
contract_version: "0.1"
---

本流程描述 `cust_company_info.cust_status`（见 [[customer_status]]）的流转，表达企业作为客户实体的经营状态：新增（`ADD`）、生效（`EFFECT`）、冻结（`FREEZE`）、注销（`WRITEOFF`），另有一个数据库分布值“变更中”（`CHANGE`）。

该状态机的入口是认证成功：认证状态迁移到 `BUILD_SUCCESS` 时联动置为 `EFFECT`，见 [[enterprise_auth_status_machine]] 与 [[auth_success_sets_customer_effective]]。生效之后可被冻结、解冻、注销；冻结与注销会连带影响该企业下的用户，见 [[freeze_company_freezes_admin]] 与 [[writeoff_company_freezes_all_users]]。生效企业还需同时满足认证状态与启用标记，口径见 [[effective_company]]。

```ground:process
name: 客户状态机
field: cust_status
states:
  - value: ADD
    label: 新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: CHANGE
    label: 变更中
    source: db_dist
transitions:
  - from: ADD
    event: 认证成功
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: EFFECT
    event: 冻结
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze"
  - from: FREEZE
    event: 解冻
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze"
  - from: EFFECT
    event: 注销
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable"
```

## 需求背景

暂无需求文档主张。本状态机与认证状态机（[[enterprise_auth_status_machine]]）通过“认证成功 → 生效”这一条联动规则耦合，其余事件（冻结/解冻/注销）独立于认证流程。

## 版本演进

- v0.1：依据语义分析建立状态机页，登记 5 个状态（4 个代码枚举值 + 1 个数据库分布值）与 4 条流转及其代码证据。

---END FILE---

---FILE: processes/operation_check_status_machine.md ---
---
type: process
title: 运营审核状态机（check_status）
page_key: operation_check_status_machine
domain: 企业建档与认证
status: draft
aliases:
  - check_status 流转
  - 运营中台审核状态机
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:submitCust
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:reSubmit
  - db:cust_company_info.check_status
contract_version: "0.1"
---

本流程描述 `cust_company_info.check_status`（见 [[check_status]]）的流转，表达**运营中台对单次提交的审核结果**，与企业的整体认证状态（[[enterprise_auth_status_machine]]）不是同一维度：前者是一次审核的结果，后者是建档全过程的状态，边界说明见 [[auth_status]]。

流转主干为：初始化 → 审核中 → 审核通过 / 退回客户；退回客户后客户可重新提交再次进入审核中。审核中同时进入认证状态机的“认证中”，审核通过 / 退回会驱动认证状态迁移为认证成功 / 待客户确认。

```ground:process
name: 运营审核状态机
field: check_status
states:
  - value: CUST_CHECK_INIT
    label: 初始化
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: db_dist
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户
    source: code_enum
  - value: EFFECT
    label: 生效
    source: db_dist
transitions:
  - from: CUST_CHECK_INIT
    event: 提交运营中台审核
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustCompanyInfoApplication.java:submitCust"
  - from: CUST_CHECK_CHECKING
    event: 运营审核通过
    to: CUST_CHECK_PASS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CHECK_CHECKING
    event: 运营审核退回
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CHECK_BACKTOCUSTOM
    event: 客户重新提交
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustCompanyInfoApplication.java:reSubmit"
```

## 需求背景

暂无需求文档主张。注意该状态集合中同时出现审核语义（`CUST_CHECK_*`）与生命周期语义（`EFFECT`），且 `CUST_CHECK_CHECKING`、`EFFECT` 来源于数据库分布而非代码枚举，说明该字段可能存在语义混用或多来源写入。

## 版本演进

- v0.1：依据语义分析建立状态机页，登记 6 个状态（4 个代码枚举值 + 2 个数据库分布值）与 4 条流转及其代码证据。

---END FILE---

---FILE: calibers/effective_company.md ---
---
type: caliber
title: 生效企业
page_key: effective_company
domain: 企业建档与认证
status: draft
aliases:
  - 租户生效企业判断
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany
contract_version: "0.1"
---

“生效企业”是跨表查询与租户判定的核心口径：只有同时满足**认证成功**（`cust_build_status = 'BUILD_SUCCESS'`，见 [[auth_status]]）、**客户生效**（`cust_status = 'EFFECT'`，见 [[customer_status]]）、**是主数据**（`data_type = '1'`，见 [[main_data]]）、**数据启用**（`enable = 'Y'`）四个条件的记录，才算作可开展业务的生效企业。

该口径被用于“租户是否有生效企业”的判断（`getTenantCodesWithEffectCompany`），因此四个条件缺一不可；只满足认证状态或客户状态单项的记录不能视为生效企业。

```ground:caliber
name: 生效企业
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1' AND cust_company_info.enable = 'Y'
scope: 企业查询、租户有生效企业判断
evidence: "code_path:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany"
```

## 需求背景

暂无需求文档主张。该口径的四个条件分别来自认证状态机（[[enterprise_auth_status_machine]]）、客户状态机（[[customer_status_machine]]）与数据类型口径（[[main_data]]），是三者交叉后的复合判定。

## 版本演进

- v0.1：依据代码证据建立口径页，条件与代码实现逐字一致。

---END FILE---

---FILE: calibers/main_data.md ---
---
type: caliber
title: 主数据
page_key: main_data
domain: 企业建档与认证
status: draft
aliases:
  - 企业主数据
oid: 1
scope:
  databases: []
sources:
  - code:CustDataTypeConstant.DATA_TYPE_MAIN
contract_version: "0.1"
---

“主数据”口径用于把同一个企业实体在 `cust_company_info` 中的**正式记录**与过程记录区分开：`data_type = '1'` 的记录代表企业主数据，是企业查询与更新的默认范围（见 [[cust_company_info]]、[[effective_company]]）。

认证/变更过程中产生的记录数据与申请数据不属于主数据，口径见 [[process_apply_data]]；主数据通过 `apply_data_id` 指向最近一次流程数据，过程数据通过 `main_data_id` 回指主数据。

```ground:caliber
name: 主数据
predicate: cust_company_info.data_type = '1'
scope: 企业主数据查询与更新
evidence: "code_path:CustDataTypeConstant.DATA_TYPE_MAIN"
```

## 需求背景

暂无需求文档主张。该口径是状态更新等写操作的前置条件之一，见 [[auth_status_conditional_update]]。

## 版本演进

- v0.1：依据代码证据建立口径页。

---END FILE---

---FILE: calibers/process_apply_data.md ---
---
type: caliber
title: 流程/申请数据
page_key: process_apply_data
domain: 企业建档与认证
status: draft
aliases:
  - 记录数据
  - 申请数据
oid: 1
scope:
  databases: []
sources:
  - code:CustDataTypeConstant.DATA_TYPE_RECORD/DATA_TYPE_APPLY
contract_version: "0.1"
---

“流程/申请数据”口径覆盖 `cust_company_info` 中 `data_type IN ('0','2')` 的记录：`0` 为记录数据（暂存/变更过程数据），`2` 为申请数据（认证流程数据）。两者合起来代表企业的过程态数据，与主数据（[[main_data]]）相对。

该口径是“在途变更”判断的基础：当存在 `data_type = '2'` 且认证状态不在成功/失败态的流程数据时，视为存在在途变更流程，见 [[change_precondition_check]]。

```ground:caliber
name: 流程/申请数据
predicate: cust_company_info.data_type IN ('0','2')
scope: 认证流程、变更流程数据
evidence: "code_path:CustDataTypeConstant.DATA_TYPE_RECORD/DATA_TYPE_APPLY"
```

## 需求背景

暂无需求文档主张。过程数据通过 `main_data_id` 关联主数据，主数据通过 `apply_data_id` 关联最近一次流程数据，二者构成双向引用。

## 版本演进

- v0.1：依据代码证据建立口径页。

---END FILE---

---FILE: calibers/pending_customer_confirm.md ---
---
type: caliber
title: 待客户确认
page_key: pending_customer_confirm
domain: 企业建档与认证
status: draft
aliases:
  - CUST_CONFIRM_AWAIT 判断
oid: 1
scope:
  databases: []
sources:
  - code:CustBuildStatusConstant.CUST_CONFIRM_AWAIT
contract_version: "0.1"
---

“待客户确认”是认证状态 `cust_build_status = 'CUST_CONFIRM_AWAIT'` 的记录集合（见 [[auth_status]]、[[enterprise_auth_status_machine]]）。处于该状态的企业已由平台或客户发起建档，等待客户侧确认或提交审核。

该状态是重新认证的唯一允许入口（见 [[reauthentication_restriction]]），同时也是运营退回后回落的目标状态；简易认证流程在该状态下可直接确认至认证成功。

```ground:caliber
name: 待客户确认
predicate: cust_company_info.cust_build_status = 'CUST_CONFIRM_AWAIT'
scope: 认证流程状态
evidence: "code_path:CustBuildStatusConstant.CUST_CONFIRM_AWAIT"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立口径页。

---END FILE---

---FILE: calibers/certifying.md ---
---
type: caliber
title: 认证中
page_key: certifying
domain: 企业建档与认证
status: draft
aliases:
  - CUST_BUILDING 判断
oid: 1
scope:
  databases: []
sources:
  - code:CustBuildStatusConstant.CUST_BUILDING
contract_version: "0.1"
---

“认证中”是认证状态 `cust_build_status = 'CUST_BUILDING'` 的记录集合（见 [[auth_status]]、[[enterprise_auth_status_machine]]）。处于该状态的企业已提交认证并进入审核环节，等待运营审核通过或退回。

该状态与运营审核状态机的“审核中”（[[operation_check_status_machine]] 的 `CUST_CHECK_CHECKING`）在业务时间上重合，但字段与判定口径不同，二者不可互相替代。

```ground:caliber
name: 认证中
predicate: cust_company_info.cust_build_status = 'CUST_BUILDING'
scope: 认证流程状态
evidence: "code_path:CustBuildStatusConstant.CUST_BUILDING"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立口径页。

---END FILE---

---FILE: concepts/auth_status.md ---
---
type: concept
title: 认证状态
page_key: auth_status
domain: 企业建档与认证
status: draft
aliases:
  - 建档状态
  - cust_build_status
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
adjudication: boundary
also_confused_with:
  - 客户状态
  - 审核状态
boundary: 认证状态描述企业建档审核的进度；客户状态描述企业生命周期状态；审核状态描述运营中台单次审核结果。
---

“认证状态”（也称建档状态）指 `cust_company_info.cust_build_status`，描述一个企业从初始化（`INIT`）到认证成功（`BUILD_SUCCESS`）/认证失败（`BUILD_FAIL`）的全流程进度。它是建档流程的主状态，流转细节见 [[enterprise_auth_status_machine]]。

该概念最容易与 [[customer_status]]（客户状态）和 [[check_status]]（审核状态）混用。裁定边界为：认证状态是企业建档审核的**整体进度**；客户状态是企业作为客户的**生命周期状态**（生效、冻结、注销）；审核状态是运营中台对**单次提交**的审核结果。三者存放于同一张表 [[cust_company_info]] 的不同字段，参与不同的判定口径（如 [[effective_company]] 同时要求认证状态与客户状态）。

## 需求背景

暂无需求文档主张。术语桥证据来源于数据库字段语义与代码枚举常量（`CustBuildStatusConstant`）。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与客户状态、审核状态的边界。

---END FILE---

---FILE: concepts/customer_status.md ---
---
type: concept
title: 客户状态
page_key: customer_status
domain: 企业建档与认证
status: draft
aliases:
  - cust_status
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_status
contract_version: "0.1"
maps_to: cust_company_info.cust_status
adjudication: boundary
also_confused_with:
  - 认证状态
boundary: 客户状态包括生效、冻结、注销等，与认证状态独立。
---

“客户状态”指 `cust_company_info.cust_status`，表达企业作为客户实体的经营状态：新增（`ADD`）、生效（`EFFECT`）、冻结（`FREEZE`）、注销（`WRITEOFF`）等。流转细节见 [[customer_status_machine]]。

它与 [[auth_status]]（认证状态）相互独立，仅在“认证成功 → 客户生效”这一条联动规则上耦合（见 [[auth_success_sets_customer_effective]]）。判断“企业是否可经营”需要同时看两个状态，见 [[effective_company]]。

## 需求背景

暂无需求文档主张。冻结、注销动作会连带影响企业下用户，见 [[freeze_company_freezes_admin]]、[[writeoff_company_freezes_all_users]]。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与认证状态的边界。

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
  databases: []
sources:
  - db:cust_company_info.identify_style
contract_version: "0.1"
maps_to: cust_company_info.identify_style
adjudication: boundary
also_confused_with:
  - 录入方式
boundary: 认证方式指 INVITE、INVITE_AGW、SELF、SIMPLE；录入方式指 AGW_BUILD、PC_BUILD、SIMPLE。
---

“认证方式”指 `cust_company_info.identify_style`，表示企业走的是哪一条**认证流程**：`INVITE`（邀请认证-客户录入）、`INVITE_AGW`（邀请认证-平台录入）、`SELF`（自主认证）、`SIMPLE`（简易认证）。

认证方式直接决定建档提交后的状态去向：`INVITE`/`SELF` 提交后进入待客户确认，`INVITE_AGW` 直接进入认证中，`SIMPLE` 走简易确认路径，见 [[enterprise_auth_status_machine]]。它常与 [[build_type]]（录入方式）混用，但后者描述的是**数据由谁录入**，不是认证流程类型；两者取值集合虽有重叠（如 `SIMPLE`），语义层面不同。

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与录入方式的边界。

---END FILE---

---FILE: concepts/build_type.md ---
---
type: concept
title: 录入方式
page_key: build_type
domain: 企业建档与认证
status: draft
aliases:
  - cust_build_type
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_build_type
contract_version: "0.1"
maps_to: cust_company_info.cust_build_type
adjudication: boundary
also_confused_with:
  - 认证方式
boundary: 录入方式表示数据由谁录入（平台/客户端/简易）；认证方式表示认证流程类型。
---

“录入方式”指 `cust_company_info.cust_build_type`，表示企业数据由谁录入：`AGW_BUILD`（平台录入）、`PC_BUILD`（客户端录入）、`SIMPLE`（简易录入）。

它与 [[identify_style]]（认证方式）经常被混用，因为二者常常同时出现在建档入口。裁定边界为：录入方式描述**数据录入主体/通道**，认证方式描述**认证流程类型**；后者决定状态机走向（见 [[enterprise_auth_status_machine]]）。

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与认证方式的边界。

---END FILE---

---FILE: concepts/company_type.md ---
---
type: concept
title: 企业类型
page_key: company_type
domain: 企业建档与认证
status: draft
aliases:
  - 企业角色
  - 客户角色
  - cust_company_type
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_company_type
contract_version: "0.1"
maps_to: cust_company_info.cust_company_type
adjudication: synonym
also_confused_with: []
boundary: 企业类型、企业角色、客户角色均指同一概念，存储为JSON数组字符串。
---

“企业类型”“企业角色”“客户角色”是同一概念的不同叫法，对应字段 `cust_company_info.cust_company_type`。该字段以 **JSON 数组字符串**存储，例如 `["SUPPLIER"]`、`["CORE"]`，说明一个企业可同时承担多个角色。

该概念在语义分析中未发现与其他术语的混淆项（`adjudication: synonym`），是一组纯同义词归一；读取时需按 JSON 数组解析，不能按单值枚举直接比较。

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据语义分析建立 concept 页，归一企业类型 / 企业角色 / 客户角色三个同义叫法。

---END FILE---

---FILE: concepts/check_status.md ---
---
type: concept
title: 审核状态
page_key: check_status
domain: 企业建档与认证
status: draft
aliases:
  - check_status
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.check_status
contract_version: "0.1"
maps_to: cust_company_info.check_status
adjudication: boundary
also_confused_with:
  - 认证状态
boundary: 审核状态是运营中台对单次提交的审核结果；认证状态是企业建档的整体状态。
---

“审核状态”指 `cust_company_info.check_status`，是**运营中台对单次提交的审核结果**，取值包括 `CUST_CHECK_INIT`、`CUST_CHECK_CHECKING`、`CUST_CHECK_PASS`、`CUST_CHECK_REJECT`、`CUST_CHECK_BACKTOCUSTOM`、`EFFECT`，流转见 [[operation_check_status_machine]]。

它与 [[auth_status]]（认证状态）维度不同：审核状态针对一次提交，认证状态覆盖企业建档全过程，因此一次审核通过并不等于认证完成链路全部结束（还需要状态机上的后续迁移）。同一张表 [[cust_company_info]] 中还存在流程实例状态 `act_procinst_status`，也带“审批”字样，需注意区分。

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与认证状态的边界。

---END FILE---

---FILE: rules/auth_success_sets_customer_effective.md ---
---
type: rule
title: 认证成功置客户生效
page_key: auth_success_sets_customer_effective
domain: 企业建档与认证
status: draft
aliases:
  - 认证成功联动生效
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
---

当企业认证状态变更为 `BUILD_SUCCESS` 时，系统同步将客户状态 `cust_status` 置为 `EFFECT`。这条规则是两个状态机（[[enterprise_auth_status_machine]] 与 [[customer_status_machine]]）之间唯一的联动点，也是企业进入“生效企业”口径（[[effective_company]]）的必要环节。

该规则意味着：客户状态的“生效”不是独立操作的结果，而是认证成功的结果；反向地，认证失败或退回不会改变客户状态。

```ground:rule
name: 认证成功置客户生效
content: 当企业认证状态变更为 BUILD_SUCCESS 时，同步将客户状态 cust_status 置为 EFFECT。
impact: 企业正式生效，可开展业务。
field_targets:
  - cust_build_status
  - cust_status
evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。

---END FILE---

---FILE: rules/freeze_company_freezes_admin.md ---
---
type: rule
title: 冻结企业同时冻结管理员
page_key: freeze_company_freezes_admin
domain: 企业建档与认证
status: draft
aliases:
  - 企业冻结连带管理员
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:freeze
contract_version: "0.1"
---

冻结企业（`cust_status` 置为 `FREEZE`，见 [[customer_status_machine]]）时，系统同时冻结该企业下的管理员用户，使管理员无法登录。这是一条**企业状态对用户状态的级联约束**，说明客户状态变更的影响范围不限于企业实体本身。

```ground:rule
name: 冻结企业同时冻结管理员
content: 冻结企业时，同时冻结该企业下的管理员用户。
impact: 管理员无法登录。
field_targets:
  - cust_status
evidence: "code_path:CustCompanyInfoApplication.java:freeze"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。

---END FILE---

---FILE: rules/writeoff_company_freezes_all_users.md ---
---
type: rule
title: 注销企业同时冻结所有用户
page_key: writeoff_company_freezes_all_users
domain: 企业建档与认证
status: draft
aliases:
  - 企业注销连带全部用户
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:custStatusOperator
contract_version: "0.1"
---

注销企业（`cust_status` 置为 `WRITEOFF`，见 [[customer_status_machine]]）时，系统先冻结该企业下的**所有用户**。与 [[freeze_company_freezes_admin]] 相比，注销的级联范围从“管理员”扩大到“全部用户”，说明注销是比冻结更强的终止性动作。

```ground:rule
name: 注销企业同时冻结所有用户
content: 注销企业时，先冻结该企业下所有用户。
impact: 所有用户无法登录。
field_targets:
  - cust_status
evidence: "code_path:CustCompanyInfoApplication.java:custStatusOperator"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。

---END FILE---

---FILE: rules/auth_status_conditional_update.md ---
---
type: rule
title: 认证状态条件更新
page_key: auth_status_conditional_update
domain: 企业建档与认证
status: draft
aliases:
  - 认证状态并发保护
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
contract_version: "0.1"
---

更新认证状态时，系统要求匹配**原状态**、`enable = 'Y'`、`data_type = '1'`（主数据，见 [[main_data]]）三个条件同时成立，才执行更新。这是一条乐观并发控制规则，用于保证认证状态机（[[enterprise_auth_status_machine]]）状态迁移的原子性，避免并发请求造成状态跳变或覆盖。

需要写认证状态时，务必带上原状态与数据类型条件，不能只按主键直接更新。

```ground:rule
name: 认证状态条件更新
content: 更新认证状态时需匹配原状态且 enable='Y' 且 data_type='1'（主数据），防止并发错误。
impact: 保证状态迁移的原子性。
field_targets:
  - cust_build_status
evidence: "code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。

---END FILE---

---FILE: rules/reauthentication_restriction.md ---
---
type: rule
title: 重新认证限制
page_key: reauthentication_restriction
domain: 企业建档与认证
status: draft
aliases:
  - 重新认证前置条件
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyOperationApplication.java:reAuthentication
contract_version: "0.1"
---

仅当认证状态为 `CUST_CONFIRM_AWAIT`（待客户确认，见 [[pending_customer_confirm]]）时，才允许将其重置为 `INIT` 以重新认证；状态不符时会抛出异常。这条规则限定了认证状态机（[[enterprise_auth_status_machine]]）中 `CUST_CONFIRM_AWAIT → INIT` 这条回退边的可执行前提。

```ground:rule
name: 重新认证限制
content: 仅当认证状态为 CUST_CONFIRM_AWAIT 时，允许重置为 INIT 重新认证。
impact: 状态不符时抛异常。
field_targets:
  - cust_build_status
evidence: "code_path:CustCompanyOperationApplication.java:reAuthentication"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。

---END FILE---

---FILE: rules/change_precondition_check.md ---
---
type: rule
title: 变更前置校验
page_key: change_precondition_check
domain: 企业建档与认证
status: draft
aliases:
  - 在途变更拦截
oid: 1
scope:
  databases: []
sources:
  - code:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
contract_version: "0.1"
---

当企业存在**在途变更流程**时，不允许发起新的变更。判定条件为：存在 `data_type = '2'`（申请数据，见 [[process_apply_data]]）的记录，且该记录的认证状态不在 `BUILD_SUCCESS` / `BUILD_FAIL` 两个终态内（见 [[enterprise_auth_status_machine]]）。

该规则用于防止并发变更，与 [[auth_status_conditional_update]] 一起构成建档/变更链路的并发保护。

```ground:rule
name: 变更前置校验
content: 企业存在在途变更流程（data_type='2' 且 cust_build_status 不在 BUILD_SUCCESS/BUILD_FAIL）时，不允许发起新的变更。
impact: 防止并发变更。
field_targets:
  - data_type
  - cust_build_status
evidence: "code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。

---END FILE---

---REVIEW: table | cust_company_info---
`scope.databases` 无法确定：语义分析只给出表名 `cust_company_info`，未给出物理库名，因此本次所有页面的 `scope.databases` 均为空数组，未做任何推断填充。请在补充物理库名后统一回填（涉及 21 个页面）。
---END REVIEW---

---REVIEW: process | 企业认证状态机（cust_build_status）---
状态集合存在两个来源：`code_enum`（9 个代码枚举值）与 `db_dist`（3 个数据库分布值：`CUST_AUDIT_AWAIT`、`BUILDING`、`CUST_BUILD_SUCCESS`）。其中 `CUST_BUILD_SUCCESS` 被标注为“认证成功（历史值）”，未确认这 3 个值是否仍在写入、还是仅存于历史数据。此外 `CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM`（待客户确认-简易认证）、`CUST_BUILDING` 与 `BUILDING` 语义高度重叠，是否为同义迁移值待确认。
---END REVIEW---

---REVIEW: process | 运营审核状态机（check_status）---
`check_status` 的取值同时包含审核结果（`CUST_CHECK_*`）与生命周期值（`EFFECT`），后者与 [[customer_status]] 的取值字面相同。`check_status` 与同表的 `act_procinst_status`（流程实例审批状态，中文取值）功能边界不明，未确认二者谁是运营审核的权威字段。
---END REVIEW---

---REVIEW: concept | 认证状态---
`cust_build_status` 取值为 `BUILD_ACTIVATE`（待激活）、`CUST_CHANGE`（变更中）两个状态在语义分析中给出，但状态机 `transitions` 中没有对应的入边或出边，未确认其触发条件与关联流程（变更流程？激活流程？）。
---END REVIEW---