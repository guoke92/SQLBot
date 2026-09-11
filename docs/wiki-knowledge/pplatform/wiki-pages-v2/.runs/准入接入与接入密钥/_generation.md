---FILE: tables/cust_access_secret.md ---
---
type: table
title: 客户接入密钥表
page_key: cust_access_secret
domain: 准入接入
status: draft
aliases: [接入密钥, 接入密钥信息, cust_access_secret]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "db: cust_access_secret 字段语义（语义分析 field_semantics）"
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java"
contract_version: "0.1"
---

`cust_access_secret` 是「准入接入与接入密钥」主题的核心主表，承载各接入渠道的密钥材料与租户归属信息。接入方以 `channel`（应用id/渠道标识）作为入口标识，系统据此取出 `db_tenant_code` 并设置租户上下文，因此该表既是鉴权入口，也是租户路由的起点。

从字段结构看，本表可划分为几组语义：

- **标识与渠道**：`id`（表主键）、`code`（编码）、`name`（名称）、`channel`（应用id/渠道标识，用于唯一标识接入渠道）。渠道语义的边界见 [[concepts/channel]]。
- **密钥材料**：`encry_type`（加密类型）、`pub_key`（公钥）、`pri_key`（私钥）、`password`（密码）、`key_num`（密钥对数量）、`rel_lls_secret_id`（关联平台密钥记录id）。这些字段共同决定了渠道侧的加解密与鉴权方式。
- **启停与备注**：`enable`（启用标识，Y=启用，N=禁用）、`remark`（备注）。启用语义见 [[concepts/enable]]，其判定口径见 [[calibers/access_secret_enable_valid]]。
- **审计字段**：`create_by` / `create_user` / `create_time` 与 `update_by` / `update_user` / `update_time`，分别记录创建与更新的人和时间。
- **流程字段**：`act_procinst_id`（流程实例ID）、`act_procinst_no`（流程申请编号）、`act_procinst_status`（当前审批状态）、`act_procinst_date`（审批结束时间），用于承载接入密钥相关审批流。
- **租户字段**：`app_tenant_code`（逻辑租户标识）、`db_tenant_code`（数据租户标识，用于多租户隔离；代码中通过渠道查询接入密钥后，用此字段设置租户上下文）。
- **机构与许可**：`organization_id`（机构编号）、`status_query_license_enabled`（建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否）。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；上述定位与字段说明全部来自库表语义与代码证据。

## 版本演进

- v0.1（本页）：依据 `cust_access_secret` 的库表字段语义与 `CustAccessApplication` 中的渠道校验代码建立首版契约，覆盖 26 个字段。字段级证据见下方锚点块。
- 与之相关的准入校验规则见 [[rules/channel_exists_and_enabled]]、[[rules/channel_tenant_exists]]、[[rules/company_build_duplicate_check]]、[[rules/tianma_company_build_duplicate_check]]。

```ground:fields
table: cust_access_secret
fields:
  - field: id
    meaning: 表主键
    evidence: db
  - field: code
    meaning: 编码
    evidence: db
  - field: name
    meaning: 名称
    evidence: db
  - field: channel
    meaning: 应用id/渠道标识，用于唯一标识接入渠道
    evidence: db
  - field: encry_type
    meaning: 加密类型
    evidence: db
  - field: pub_key
    meaning: 公钥
    evidence: db
  - field: pri_key
    meaning: 私钥
    evidence: db
  - field: password
    meaning: 密码
    evidence: db
  - field: key_num
    meaning: 密钥对数量
    evidence: db
  - field: rel_lls_secret_id
    meaning: 关联平台密钥记录id
    evidence: db
  - field: enable
    meaning: 启用标识，Y=启用，N=禁用
    evidence: db
  - field: remark
    meaning: 备注
    evidence: db
  - field: create_by
    meaning: 创建人id
    evidence: db
  - field: create_user
    meaning: 创建人名称
    evidence: db
  - field: create_time
    meaning: 创建时间
    evidence: db
  - field: update_by
    meaning: 更新人id
    evidence: db
  - field: update_user
    meaning: 更新人名称
    evidence: db
  - field: update_time
    meaning: 更新时间
    evidence: db
  - field: act_procinst_id
    meaning: 流程实例ID
    evidence: db
  - field: app_tenant_code
    meaning: 逻辑租户标识
    evidence: db
  - field: db_tenant_code
    meaning: 数据租户标识，用于多租户隔离；代码中通过渠道查询接入密钥后，用此字段设置租户上下文
    evidence: db
  - field: act_procinst_no
    meaning: 流程申请编号
    evidence: db
  - field: act_procinst_status
    meaning: 当前审批状态
    evidence: db
  - field: act_procinst_date
    meaning: 审批结束时间
    evidence: db
  - field: organization_id
    meaning: 机构编号
    evidence: db
  - field: status_query_license_enabled
    meaning: 建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否
    evidence: db
```
---END FILE---

---FILE: processes/cust_company_info_cust_build_status.md ---
---
type: process
title: 企业建档状态机
page_key: cust_company_info.cust_build_status
domain: 准入接入
status: draft
aliases: [cust_build_status, 建档状态, 企业建档]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustCompanyInfoApplication.java:getCustBuildStatus"
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
contract_version: "0.1"
---

企业建档状态机描述 `cust_company_info.cust_build_status` 在准入建档流程中的取值与流转。它是准入接入的“结果态”部分：接入渠道通过 [[tables/cust_access_secret]] 完成校验后，企业主体才进入建档流程，并在邀约认证、自主认证、平台录入等不同入口下经历不同的状态路径。

状态分为三类语义：**初始与失败态**（`INIT` 初始化/待提交、`BUILD_FAIL` 建档失败）、**确认/审核中间态**（`CUST_CONFIRM_AWAIT` 待客户确认、`CUST_BUILDING` 客户提交后运营审核中、`AWAIT_CUST_CONFIRM` 等待客户确认（简易认证场景）、`BUILDING` 建档中）、**终态**（`BUILD_SUCCESS` 建档成功）。其中 `AWAIT_CUST_CONFIRM` 与 `CUST_CONFIRM_AWAIT` 语义接近但分别对应简易认证场景与常规确认场景，使用时需区分。

流转上，信息提交（邀请认证-客户录入/自主认证）可从 `INIT` 或 `BUILD_FAIL` 进入 `CUST_CONFIRM_AWAIT`；客户提交后进入 `CUST_BUILDING`；运营中台审核退回、以及邀请认证-平台录入路径下审核通过，都会回到 `CUST_CONFIRM_AWAIT`；平台录入客户点击确认提交后进入 `BUILD_SUCCESS`。此外，运营中台审核通过可从任意状态（`*`）直达 `BUILD_SUCCESS`，审核拒绝可从任意状态直达 `BUILD_FAIL`。

该状态字段同时是重复建档校验的判据之一：见 [[rules/company_build_duplicate_check]]、[[rules/tianma_company_build_duplicate_check]] 与口径 [[calibers/company_build_dedup_exclude]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；状态与迁移均来自代码枚举与消息处理逻辑。

## 版本演进

- v0.1（本页）：依据 `getCustBuildStatus`、`checkMsg` 中的枚举与迁移判断，登记 7 个状态与 8 条迁移。`BUILDING` 与 `AWAIT_CUST_CONFIRM` 两个状态的源码出处见下方 REVIEW 提示。

```ground:states
machine: 企业建档状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化/待提交
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 客户提交后运营审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILDING
    label: 建档中
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 等待客户确认（简易认证场景）
    source: code_enum
```

```ground:transitions
machine: 企业建档状态机
transitions:
  - from: INIT
    event: 信息提交（邀请认证-客户录入/自主认证）
    to: CUST_CONFIRM_AWAIT
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: BUILD_FAIL
    event: 信息提交（邀请认证-客户录入/自主认证）
    to: CUST_CONFIRM_AWAIT
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交
    to: CUST_BUILDING
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
  - from: CUST_BUILDING
    event: 运营中台审核通过（邀请认证-平台录入）
    to: CUST_CONFIRM_AWAIT
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
  - from: CUST_CONFIRM_AWAIT
    event: 平台录入客户点击确认提交
    to: BUILD_SUCCESS
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
  - from: "*"
    event: 运营中台审核通过
    to: BUILD_SUCCESS
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
  - from: "*"
    event: 运营中台审核拒绝
    to: BUILD_FAIL
    evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/msg/CustAuditMsgService.java:checkMsg"
```
---END FILE---

---FILE: calibers/access_secret_enable_valid.md ---
---
type: caliber
title: 接入密钥有效性
page_key: access_secret_enable_valid
domain: 准入接入
status: draft
aliases: [启用口径, enable='Y', 密钥有效性]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
---

「接入密钥有效性」是准入校验的第一道口径：判定一条 [[tables/cust_access_secret]] 记录是否处于可用状态。口径为 `enable = 'Y'`，作用域限定在接入密钥查询环节。

需要注意的是，该口径只回答“密钥是否启用”，不回答“渠道是否存在”——渠道存在性由 [[calibers/channel_lookup]] 与 [[rules/channel_exists_and_enabled]] 共同约束；两者串联后，才能得出“某渠道当前可接入”的结论。术语边界见 [[concepts/enable]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；口径定义来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版口径，来源为 `validateSetValue`。

```ground:caliber
name: 接入密钥有效性
predicate: "cust_access_secret.enable = 'Y'"
scope: 接入密钥查询
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```
---END FILE---

---FILE: calibers/channel_lookup.md ---
---
type: caliber
title: 渠道查询
page_key: channel_lookup
domain: 准入接入
status: draft
aliases: [渠道口径, channel 查询, 按渠道取租户]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:getDbTenantCode"
contract_version: "0.1"
---

「渠道查询」定义准入接入时如何由渠道定位租户：以 `cust_access_secret.channel = '渠道值'` 检索 [[tables/cust_access_secret]]，命中记录的 `db_tenant_code` 即为后续请求需要设置的租户上下文。

该口径是租户路由的前置步骤，其输出被 [[rules/channel_tenant_exists]] 继续用于校验租户配置是否可用。渠道术语本身见 [[concepts/channel]]，密钥术语见 [[concepts/access_secret]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；口径定义来自 `CustAccessApplication.getDbTenantCode` 的代码证据。

## 版本演进

- v0.1（本页）：首版口径，来源为 `getDbTenantCode`。

```ground:caliber
name: 渠道查询
predicate: "cust_access_secret.channel = '渠道值'"
scope: 根据渠道获取租户编码
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:getDbTenantCode"
```
---END FILE---

---FILE: calibers/company_build_dedup_exclude.md ---
---
type: caliber
title: 企业重复建档排除条件
page_key: company_build_dedup_exclude
domain: 准入接入
status: draft
aliases: [重复建档排除, cust_build_status != BUILD_FAIL]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
---

「企业重复建档排除条件」是重复建档校验的取数口径：判定“已存在企业”时，只统计 `cust_company_info.cust_build_status != 'BUILD_FAIL'` 的记录。也就是说，处于建档失败态的企业不算作“已建档”，允许重新发起。

该口径服务于 [[rules/company_build_duplicate_check]] 与 [[rules/tianma_company_build_duplicate_check]]；与状态取值的关系见流程页 [[processes/cust_company_info_cust_build_status]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；口径定义来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版口径，来源为 `validateSetValue`。

```ground:caliber
name: 企业重复建档排除条件
predicate: "cust_company_info.cust_build_status != 'BUILD_FAIL'"
scope: 企业重复建档校验
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```
---END FILE---

---FILE: concepts/channel.md ---
---
type: concept
title: 渠道
page_key: term.channel
domain: 准入接入
status: draft
aliases: [channel, 应用id]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:getDbTenantCode"
contract_version: "0.1"
maps_to: cust_access_secret.channel
also_confused_with: []
adjudication: synonym
---

「渠道」在业务语境中与 `channel`、`应用id` 同义，落库位置为 [[tables/cust_access_secret]] 的 `channel` 字段。其边界是：渠道指接入方标识，存储在 channel 字段；它不等于租户——渠道记录上挂载的 `db_tenant_code` 才是租户标识，由 [[calibers/channel_lookup]] 取出后用于设置租户上下文。

接入侧一切校验都以渠道为起点：先按渠道查密钥记录，再判断启用与租户配置，见 [[rules/channel_exists_and_enabled]]、[[rules/channel_tenant_exists]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；术语判定为同义（synonym），依据代码中按 channel 检索接入密钥的用法。

## 版本演进

- v0.1（本页）：首版术语桥，判定为同义，无易混术语。
---END FILE---

---FILE: concepts/access_secret.md ---
---
type: concept
title: 接入密钥
page_key: term.access_secret
domain: 准入接入
status: draft
aliases: [密钥, cust_access_secret]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "db: cust_access_secret 字段语义"
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
maps_to: cust_access_secret
also_confused_with: [接入密钥信息]
adjudication: synonym
---

「接入密钥」与「密钥」同义，落库为 [[tables/cust_access_secret]]。其边界是：接入密钥信息表，包含公私钥等；即该词指整条密钥记录（含渠道、租户、启停与密钥材料字段），而非单指 `pub_key`/`pri_key` 某一列。

「接入密钥信息」被登记为易混说法：它在口语中有时指记录本身、有时指记录中的密钥材料部分，判断口径见 [[calibers/access_secret_enable_valid]] 与 [[concepts/enable]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；术语判定为同义（synonym）。

## 版本演进

- v0.1（本页）：首版术语桥，易混术语登记为「接入密钥信息」。
---END FILE---

---FILE: concepts/enable.md ---
---
type: concept
title: 启用
page_key: term.enable
domain: 准入接入
status: draft
aliases: [enable, 有效]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
maps_to: "cust_access_secret.enable = 'Y'"
also_confused_with: []
adjudication: synonym
---

「启用」与 `enable`、「有效」同义，语义落点为 `cust_access_secret.enable = 'Y'`。其边界是：Y 表示启用，N 表示禁用；因此“有效”在准入语境下等价于 `enable = 'Y'`，而不是泛指记录存在。

该术语对应口径 [[calibers/access_secret_enable_valid]]，并在 [[rules/channel_exists_and_enabled]] 中被用于决定是否放行渠道接入。字段清单见 [[tables/cust_access_secret]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；术语判定为同义（synonym）。

## 版本演进

- v0.1（本页）：首版术语桥，明确 Y/N 边界，无易混术语。
---END FILE---

---FILE: rules/channel_exists_and_enabled.md ---
---
type: rule
title: 渠道存在且启用校验
page_key: rule.channel_exists_and_enabled
domain: 准入接入
status: draft
aliases: [渠道校验, 渠道不存在]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
---

接入请求进入后，系统按请求中的渠道标识检索 [[tables/cust_access_secret]]：记录必须存在，且 `enable = 'Y'`；任一条件不满足即抛出“渠道不存在”异常，请求被拒绝。

这条规则是准入链路的入口闸门，阻止非法渠道接入。它依赖术语 [[concepts/channel]] 与 [[concepts/enable]]，以及口径 [[calibers/channel_lookup]]、[[calibers/access_secret_enable_valid]]；通过后进入 [[rules/channel_tenant_exists]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValue`。

```ground:rule
name: 渠道存在且启用校验
content: 根据请求中的channel查询cust_access_secret，必须存在且enable='Y'，否则抛出'渠道不存在'异常
impact: 阻止非法渠道接入
field_targets:
  - cust_access_secret.channel
  - cust_access_secret.enable
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```
---END FILE---

---FILE: rules/channel_tenant_exists.md ---
---
type: rule
title: 渠道所属租户存在校验
page_key: rule.channel_tenant_exists
domain: 准入接入
status: draft
aliases: [租户校验, 渠道所属租户不存在]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
---

渠道命中后，系统取其 `cust_access_secret.db_tenant_code`（见口径 [[calibers/channel_lookup]]），再去 `tenant_setting_config` 中查找对应租户配置：记录必须存在且 `enable = 'Y'`，否则抛出“渠道所属租户不存在”。

该规则确保租户配置完整，是 [[rules/channel_exists_and_enabled]] 之后的第二道闸门。注意它校验的是租户配置表的 `enable`，与接入密钥表的 `enable` 是两张表上的同名同义字段，判定时不可混用。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValue`；涉及的 `tenant_setting_config` 表字段级语义见页末 REVIEW 提示。

```ground:rule
name: 渠道所属租户存在校验
content: 根据渠道获取db_tenant_code后，查询TenantSettingConfig，必须存在且enable='Y'，否则抛出'渠道所属租户不存在'
impact: 确保租户配置完整
field_targets:
  - cust_access_secret.db_tenant_code
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.enable
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```
---END FILE---

---FILE: rules/company_build_duplicate_check.md ---
---
type: rule
title: 企业重复建档校验
page_key: rule.company_build_duplicate_check
domain: 准入接入
status: draft
aliases: [重复建档, 企业已建档]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
---

在同一租户下，若统一社会信用代码已存在于 `cust_company_info`，且该企业的建档状态不满足排除条件，则判定为重复建档，抛出“企业已建档！”。

“已存在”的取数口径不是“存在即可”，而是 [[calibers/company_build_dedup_exclude]]：只有 `cust_build_status != 'BUILD_FAIL'` 的记录才计入，建档失败的企业允许重新发起。状态取值与流转见 [[processes/cust_company_info_cust_build_status]]。针对天马渠道还有更细的分支，见 [[rules/tianma_company_build_duplicate_check]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValue`。

```ground:rule
name: 企业重复建档校验
content: 同一租户下，统一社会信用代码已存在且cust_build_status != 'BUILD_FAIL'时，抛出'企业已建档！'
impact: 防止重复建档
field_targets:
  - cust_company_info.certification_no
  - cust_company_info.db_tenant_code
  - cust_company_info.cust_build_status
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```
---END FILE---

---FILE: rules/tianma_company_build_duplicate_check.md ---
---
type: rule
title: 天马渠道企业重复建档校验
page_key: rule.tianma_company_build_duplicate_check
domain: 准入接入
status: draft
aliases: [天马渠道建档校验, 已通过其他方式完成建档, 正在通过其他方式建档]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValueOfTianma"
contract_version: "0.1"
---

天马渠道走独立的重复建档校验分支：与通用规则只比对统一社会信用代码不同，这里同时校验企业名称与统一社会信用代码。若命中已存在且非 `BUILD_FAIL` 的记录，则按 `cust_build_status` 的取值抛出不同提示——状态为 `BUILD_SUCCESS` 时提示“已通过其他方式完成建档”，其他状态提示“正在通过其他方式建档”。

其效果仍是防止重复建档，但把“失败态可重建”的口径 [[calibers/company_build_dedup_exclude]] 与状态机 [[processes/cust_company_info_cust_build_status]] 的取值差异显式暴露为不同话术。通用分支见 [[rules/company_build_duplicate_check]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValueOfTianma` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValueOfTianma`。

```ground:rule
name: 天马渠道企业重复建档校验
content: 对于天马渠道，校验企业名称和统一社会信用代码，如果已存在且非BUILD_FAIL，则根据cust_build_status抛出不同异常（BUILD_SUCCESS：已通过其他方式完成建档；其他：正在通过其他方式建档）
impact: 防止重复建档
field_targets:
  - cust_company_info.name
  - cust_company_info.certification_no
  - cust_company_info.db_tenant_code
  - cust_company_info.cust_build_status
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValueOfTianma"
```
---END FILE---

---REVIEW: table | cust_company_info / tenant_setting_config 字段级语义缺失---
语义分析中 `cust_company_info` 与 `tenant_setting_config` 仅以 `field_targets` 的形式出现在规则和状态机证据里（如 `cust_company_info.cust_build_status`、`tenant_setting_config.enable`），未提供字段清单与字段含义，因此本次未为这两张表产出 `tables/` 页面（写 ground:fields 会构成发明）。待补充库表语义后，再补建这两个 table 页，并与 [[tables/cust_access_secret]] 建立关联。
---END REVIEW---

---REVIEW: process | 企业建档状态机状态枚举出处待确认---
状态 `BUILDING`（建档中）与 `AWAIT_CUST_CONFIRM`（等待客户确认（简易认证场景））的 `source` 标注为 `code_enum`，但迁移证据集中在 `CustCompanyInfoApplication:getCustBuildStatus` 与 `CustAuditMsgService:checkMsg` 两处；两者具体由哪段枚举或分支定义尚未定位到行级证据，需后续确认，避免与 `CUST_CONFIRM_AWAIT`、`CUST_BUILDING` 的语义边界混淆。[[processes/cust_company_info_cust_build_status]]
---END REVIEW---