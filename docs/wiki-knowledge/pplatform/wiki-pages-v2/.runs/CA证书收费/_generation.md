---FILE: tables/ca_fee_company.md ---
---
type: table
title: ca_fee_company CA服务费企业台账
page_key: tables/ca_fee_company
domain: CA证书收费
status: draft
aliases: [CA服务费企业表, 企业缴费台账, ca_fee_company]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - code:CaFeeRuleEngineService.java
  - code:CaFeeRenewalService.java
contract_version: "0.1"
---

# ca_fee_company CA服务费企业台账

## 业务定位

`ca_fee_company` 是 CA 证书收费域的**企业级主台账**，以[[concepts/unified_social_credit_code|统码]]为唯一标识，登记某一家企业在某个收费项目下的 CA 服务状态、缴费状态、服务周期、年费口径与特殊配置快照。它同时承担两个角色：一是**拦截判定的输入**（门户校验与规则引擎读取本表判断是否放行），二是**账期状态的落点**（服务到期、续费提醒等时点被回写在本表）。

企业的**应收年费**并非只由本表决定，需结合[[tables/ca_fee_project_config]]中的项目角色价，按[[rules/annual_fee_pricing_rule|年费定价规则]]解析；企业维度的缴费状态流转见[[processes/ca_fee_company_pay_status]]，续费待办生成与复位见[[processes/ca_fee_renew_remind]]。

字段层的语义与取值约定见下方锚点块；本表不承载订单与支付流水，交易侧请见[[tables/ca_fee_order]]。

## 需求背景

本页汇总的是**库表与代码两侧可核对的字段语义**，未纳入需求文档主张（本次语义分析未提供 reqdoc 锚点证据）。业务人员对"统码""核企/供应商""年费锁定"等术语的理解差异，见[[concepts/ca_certificate_fee]]与[[concepts/core_enterprise]]。

## 版本演进

- 本次语义分析未提供与本表相关的需求文档变更主张（uncovered），故无 `(document_claim，未证实)` 条目可归档。

```ground:columns
table: ca_fee_company
columns:
  - field: certification_no
    meaning: 统一社会信用代码，企业唯一标识（统码）
    evidence: db
  - field: company_name
    meaning: 企业名称
    evidence: db
  - field: ca_status
    meaning: CA签章状态，来自签章中台（如 NORMAL/CANCELLED/UNKNOWN）
    evidence: db
  - field: pay_status
    meaning: 缴费状态：PAID 已缴费 / UNPAID 未缴费
    evidence: db
  - field: service_start
    meaning: 当前 CA 服务费服务周期起始日（含）
    evidence: db
  - field: service_end
    meaning: 当前 CA 服务费服务周期截止日（含）
    evidence: db
  - field: locked_annual_fee
    meaning: 首次缴费成功后锁定的年费标准（元）
    evidence: db
  - field: special_annual_fee
    meaning: 特殊配置后应缴年费（元）
    evidence: db
  - field: special_config_flag
    meaning: 是否存在生效中的特殊配置快照：Y/N
    evidence: db
  - field: fee_locked
    meaning: 是否已锁定年费标准：Y/N
    evidence: db
  - field: renew_remind_sent
    meaning: 本期续费待办是否已生成：Y 已生成 / N 未生成
    evidence: db
  - field: source_company_type
    meaning: 首次锁定来源企业角色，如 SUPPLIER/CORE
    evidence: db
  - field: source_project_id
    meaning: 首次锁定来源项目 ID
    evidence: db
  - field: enable
    meaning: 逻辑启用标识：Y 有效 / N 无效
    evidence: db
```

相关口径：[[calibers/paid_company]]、[[calibers/unpaid_company]]、[[calibers/enabled_company]]、[[calibers/in_service_period]]、[[calibers/expiring_soon]]、[[calibers/service_expired]]、[[calibers/whitelist_exempt]]、[[calibers/targeted_reduction]]、[[calibers/chargeable_company_role]]。

---END FILE---

---FILE: tables/ca_fee_order.md ---
---
type: table
title: ca_fee_order CA服务费订单表
page_key: tables/ca_fee_order
domain: CA证书收费
status: draft
aliases: [CA服务费订单, 缴费订单, ca_fee_order]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeePaymentApplication.java
  - code:CaFeeOrderApplication.java
contract_version: "0.1"
---

# ca_fee_order CA服务费订单表

## 业务定位

`ca_fee_order` 是 CA 证书收费的交易单据表：一次首次缴费、到期续费或存量补录对应一条订单，记录**应缴年费、实缴金额、支付方式、收费协议签署信息与交e保划扣流水号**。订单是本域唯一的"付款凭据"，企业侧的账期状态（[[tables/ca_fee_company]]）在订单支付成功后回写。

订单类型区分首次与续费场景（`order_type`），订单状态流转见[[processes/ca_fee_order_state]]。发起支付前必须满足[[rules/payment_precondition_rule|支付前置条件规则]]：订单处于 `PENDING` 且 `agreement_signed='Y'`；协议签署状态自身的流转见[[processes/ca_fee_agreement_sign]]。交e保（[[concepts/bocom]]）是当前唯一支付渠道，其划扣结果落在 `bocom_txn_sts`，对应口径[[calibers/bocom_success]]、[[calibers/bocom_pending_investigation]]、[[calibers/bocom_failure]]。

注意 `order_status` 存在**代码枚举与实际库值不一致**的情况：代码声明 `PENDING/PAID/CLOSED/EXPIRED`，而库中实际出现 `PAIDING`、`UNPAID` 等超出枚举的值。统计口径请以口径页明确取值，不要直接按代码枚举枚举全集。

## 需求背景

本页字段语义来自库表与代码两侧证据，本次语义分析未提供需求文档主张（reqdoc 锚点），故无"双源"证据条目。关开关、手动关闭、服务到期三类关闭原因的业务触发见[[processes/ca_fee_order_state]]与[[rules/renew_remind_rule]]。

## 版本演进

- 本次语义分析未提供与本表相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:columns
table: ca_fee_order
columns:
  - field: order_status
    meaning: 订单状态：PENDING 未缴费 / PAID 已缴费 / CLOSED 已关闭 / EXPIRED 已过期（代码枚举）；DB 实际存在 PAIDING、UNPAID 等超出枚举的值
    evidence: db
  - field: order_type
    meaning: 订单类型：FIRST 首次缴费 / RENEW 即将到期续费 / RENEW_EXPIRED 已到期续费 / STOCK 存量补录
    evidence: code
  - field: annual_fee
    meaning: 应缴年费（元）
    evidence: db
  - field: pay_amount
    meaning: 实缴金额（元）
    evidence: code
  - field: pay_method
    meaning: 支付方式，当前为 BOCOM（交e保）
    evidence: code
  - field: agreement_signed
    meaning: 是否已签署收费协议：Y/N
    evidence: db
  - field: agreement_version
    meaning: 签署时绑定的收费协议版本号，如 V1.0
    evidence: db
  - field: agreement_sign_time
    meaning: 收费协议签署时间
    evidence: db
  - field: agreement_file_path
    meaning: 签章后协议文件 COS 路径
    evidence: db
  - field: bocom_txn_sts
    meaning: 交e保交易状态：00 成功 / 01 失败 / 02 待查证等
    evidence: db
  - field: bocom_plfm_ser_no
    meaning: 交e保平台流水号
    evidence: db
  - field: bocom_plfm_bsn_id
    meaning: 平台业务编号
    evidence: db
  - field: bocom_req_sn
    meaning: 请求流水号
    evidence: db
  - field: invoice_status
    meaning: 发票状态：NONE/PENDING/ISSUED/FAILED
    evidence: code
  - field: close_reason
    meaning: 关闭原因（关开关/手动关闭/服务到期等）
    evidence: db
  - field: company_type
    meaning: 企业角色：SUPPLIER/CORE/PROJECT_COMPANY
    evidence: db
```

相关口径：[[calibers/pending_order]]、[[calibers/paid_order]]、[[calibers/agreement_signed_order]]、[[calibers/bocom_success]]、[[calibers/bocom_pending_investigation]]、[[calibers/bocom_failure]]。

---END FILE---

---FILE: tables/ca_fee_project_config.md ---
---
type: table
title: ca_fee_project_config CA收费项目配置表
page_key: tables/ca_fee_project_config
domain: CA证书收费
status: draft
aliases: [CA收费项目配置, 项目收费开关配置, ca_fee_project_config]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_project_config
  - code:CaFeeRuleEngineService.java
  - code:CaFeePaymentCheckApplication.java
contract_version: "0.1"
---

# ca_fee_project_config CA收费项目配置表

## 业务定位

`ca_fee_project_config` 是 CA 证书收费的**项目级策略表**：它决定某个项目是否开启 CA 收费（`charge_enabled`）、核企与供应商各自的年费标准（`core_annual_fee` / `supplier_annual_fee`）、特殊企业名单（白名单、定向减免、延期支付），以及**哪些业务场景需要拦截**（`block_scene_list`）。

这张表是[[rules/rule_engine_priority|规则引擎优先级]]的第一道判断：项目未开启收费即整体放行；也是[[rules/intercept_scene_rule|拦截场景规则]]的唯一字段来源——即便判定需缴费，只有当前请求场景命中 `block_scene_list` 才会真正阻断业务节点。年费取值优先级见[[rules/annual_fee_pricing_rule]]，与[[tables/ca_fee_company]]中的特殊/锁定年费共同决定订单 `annual_fee`。

## 需求背景

本页字段语义来自库表与代码两侧证据，本次语义分析未提供需求文档主张（reqdoc 锚点）。"特殊企业配置"如何落到企业维度快照（`special_config_flag` / `special_annual_fee`）见[[rules/multi_project_exemption_rule]]与企业表[[tables/ca_fee_company]]。

## 版本演进

- 本次语义分析未提供与本表相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:columns
table: ca_fee_project_config
columns:
  - field: charge_enabled
    meaning: 项目是否开启 CA 收费：Y/N
    evidence: code
  - field: core_annual_fee
    meaning: 核心企业年费（元）
    evidence: code
  - field: supplier_annual_fee
    meaning: 供应商年费（元）
    evidence: code
  - field: special_company_list
    meaning: 特殊企业配置 JSON 列表（白名单/定向减免/延期支付）
    evidence: code
  - field: block_scene_list
    meaning: 收费拦截场景列表
    evidence: code
```

相关口径：[[calibers/charge_enabled_project]]；相关规则：[[rules/intercept_scene_rule]]、[[rules/annual_fee_pricing_rule]]、[[rules/rule_engine_priority]]。

---END FILE---

---FILE: processes/ca_fee_order_state.md ---
---
type: process
title: CA服务费订单状态机
page_key: processes/ca_fee_order_state
domain: CA证书收费
status: draft
aliases: [订单状态流转, order_status 状态机, CA订单状态]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeePaymentApplication.java
  - code:CaFeeOrderApplication.java
  - code:CaFeeLedgerOperateService.java
  - code:CaFeeRenewalService.java
contract_version: "0.1"
---

# CA服务费订单状态机

## 业务定位

本页描述[[tables/ca_fee_order]]中 `order_status` 的生命周期。订单从 `PENDING`（未缴费）出发，仅有四条已证实出口：**缴费成功转 `PAID`**；**手动/系统关闭、批量加白名单、服务到期处理**三条路径转入 `CLOSED`。

`PAID` 之后的状态变更（如发票、退费）在本次语义分析中**没有代码证据**，不在本页断言。此外，库中实际存在 `PAIDING`、`UNPAID` 两个代码枚举未声明的值，说明存在其他写入路径或历史数据，需以口径页而非枚举全集来统计。

支付成功的前置条件（`PENDING` + `agreement_signed='Y'`）见[[rules/payment_precondition_rule]]，协议签署自身的状态机见[[processes/ca_fee_agreement_sign]]，服务到期关闭 RENEW 待缴单的时点背景见[[rules/renew_remind_rule]]。待支付、已支付两个统计口径见[[calibers/pending_order]]与[[calibers/paid_order]]。

## 需求背景

本页为代码侧状态流转的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。"批量加白名单"与"服务到期"两条进入 `CLOSED` 的路径属于系统动作，与人工关闭在业务语义上不同，但均落在同一终态。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: CA服务费订单状态机
field: ca_fee_order.order_status
states:
  - value: PENDING
    label: 未缴费
    source: code_enum
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: CLOSED
    label: 已关闭
    source: code_enum
  - value: EXPIRED
    label: 已过期
    source: code_enum
  - value: PAIDING
    label: 支付中（DB实际存在，代码未声明）
    source: db_dist
  - value: UNPAID
    label: 未缴费（DB实际存在，代码未声明）
    source: db_dist
transitions:
  - from: PENDING
    event: 缴费成功 markPaid
    to: PAID
    evidence: "code_path:CaFeePaymentApplication.java:handlePaySuccess"
  - from: PENDING
    event: 手动/系统关闭订单 closeOrder
    to: CLOSED
    evidence: "code_path:CaFeeOrderApplication.java:closeOrder"
  - from: PENDING
    event: 批量加白名单
    to: CLOSED
    evidence: "code_path:CaFeeLedgerOperateService.java:applyWhitelist"
  - from: PENDING
    event: 服务到期处理关闭RENEW待缴单
    to: CLOSED
    evidence: "code_path:CaFeeRenewalService.java:processServiceExpired"
```

---END FILE---

---FILE: processes/ca_fee_company_pay_status.md ---
---
type: process
title: 企业缴费状态机
page_key: processes/ca_fee_company_pay_status
domain: CA证书收费
status: draft
aliases: [pay_status 状态机, 企业缴费状态流转]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - code:CaFeeRenewalService.java
contract_version: "0.1"
---

# 企业缴费状态机

## 业务定位

本页描述[[tables/ca_fee_company]]中 `pay_status` 的两态模型：`PAID`（已缴费）与 `UNPAID`（未缴费），是"企业当前是否欠费"的**最直接判据**，也是[[calibers/paid_company]]、[[calibers/unpaid_company]]两个统计口径的字段来源。

已证实的流转只有一条：**服务到期处理 `markServiceExpired` 将 `PAID` 置为 `UNPAID`**。反向的 `UNPAID → PAID`（即缴费成功回写）在本次语义分析中未见状态机条目，但其业务结果由[[processes/ca_fee_order_state]]中订单转 `PAID` 承载，请勿仅凭本页断言企业状态与订单状态必然同刻同步。

该状态不随时间自动回退：企业不欠费不等于服务仍在有效期内，判断"服务期内"须用[[calibers/in_service_period]]（`service_end >= CURDATE()`）。

## 需求背景

本页为代码侧状态流转的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。到期置为 `UNPAID` 与续费待办复位（[[processes/ca_fee_renew_remind]]）通常在同一次到期处理中被触发。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: 企业缴费状态机
field: ca_fee_company.pay_status
states:
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: UNPAID
    label: 未缴费
    source: code_enum
transitions:
  - from: PAID
    event: 服务到期处理 markServiceExpired
    to: UNPAID
    evidence: "code_path:CaFeeRenewalService.java:markServiceExpired"
```

---END FILE---

---FILE: processes/ca_fee_agreement_sign.md ---
---
type: process
title: 收费协议签署状态机
page_key: processes/ca_fee_agreement_sign
domain: CA证书收费
status: draft
aliases: [agreement_signed 状态机, 协议签署状态流转]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeeAgreementApplication.java
contract_version: "0.1"
---

# 收费协议签署状态机

## 业务定位

本页描述[[tables/ca_fee_order]]中 `agreement_signed` 的 Y/N 两态：`N`（未签署）→ 经签署动作 `signAgreement` → `Y`（已签署）。该标志是**支付的前置门槛**，与 `order_status='PENDING'` 一起构成[[rules/payment_precondition_rule]]的准入条件；不满足即无法发起交e保划扣。

签署时会绑定协议版本号（`agreement_version`，如 V1.0）与签署时间（`agreement_sign_time`），签章后的协议文件存放在 COS 路径（`agreement_file_path`）。可统计口径见[[calibers/agreement_signed_order]]。状态取值来自库分布（`db_dist`），代码中未声明为枚举。

## 需求背景

本页为代码侧签署动作与库侧取值的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。协议版本号与协议模板的治理关系（模板升级是否回溯存量订单）无证据，不做断言。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: 收费协议签署状态机
field: ca_fee_order.agreement_signed
states:
  - value: N
    label: 未签署
    source: db_dist
  - value: Y
    label: 已签署
    source: db_dist
transitions:
  - from: N
    event: 签署收费协议 signAgreement
    to: Y
    evidence: "code_path:CaFeeAgreementApplication.java:signAgreement"
```

---END FILE---

---FILE: processes/ca_fee_renew_remind.md ---
---
type: process
title: 续费提醒发送状态机
page_key: processes/ca_fee_renew_remind
domain: CA证书收费
status: draft
aliases: [renew_remind_sent 状态机, 续费待办生成状态]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - code:CaFeeRenewalService.java
contract_version: "0.1"
---

# 续费提醒发送状态机

## 业务定位

本页描述[[tables/ca_fee_company]]中 `renew_remind_sent` 的 Y/N 两态，用于**防止同一服务周期内重复推送续费待办**：`N`（未生成）表示本期还没发过续费提醒；生成续费待办后置 `Y`（已生成）。

这是一个**可复位**的状态：服务到期处理 `markServiceExpired` 会把它从 `Y` 复位为 `N`，为下一个服务周期的提醒做准备。因此该字段不能用来判断"历史上是否发过提醒"，只能表示**当前周期是否已发**。触发条件（`service_end` 距今 ≤7 天且 `renew_remind_sent='N'`）见[[rules/renew_remind_rule]]，对应口径[[calibers/expiring_soon]]；推送通道语义见[[concepts/todo]]。

## 需求背景

本页为代码侧状态流转的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。"待办"与站内信、邮件的边界见[[concepts/todo]]。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: 续费提醒发送状态机
field: ca_fee_company.renew_remind_sent
states:
  - value: N
    label: 未生成
    source: db_dist
  - value: Y
    label: 已生成
    source: db_dist
transitions:
  - from: N
    event: 续费待办生成 markRenewRemindSent
    to: Y
    evidence: "code_path:CaFeeRenewalService.java:markRenewRemindSent"
  - from: Y
    event: 服务到期处理 markServiceExpired
    to: N
    evidence: "code_path:CaFeeRenewalService.java:markServiceExpired"
```

---END FILE---

---FILE: concepts/ca_certificate_fee.md ---
---
type: concept
title: CA证书收费
page_key: concepts/ca_certificate_fee
domain: CA证书收费
status: draft
aliases: [CA服务费, CA收费, CA证书服务费]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - db:ca_fee_company
  - db:ca_fee_project_config
  - code:cafee 包
contract_version: "0.1"
maps_to: ca_fee_order、ca_fee_company、ca_fee_project_config 等表及 cafee 包
field_targets:
  - ca_fee_order.order_status
  - ca_fee_company.pay_status
  - ca_fee_project_config.charge_enabled
adjudication: synonym
also_confused_with: [CFCA认证, CA认证, 电子签章]
---

# CA证书收费

## 业务定位

本模块的 **CA 证书收费**指：对使用电子认证服务（CA 证书）的企业收取服务费。它的物化载体是三张表——订单（[[tables/ca_fee_order]]）、企业台账（[[tables/ca_fee_company]]）、项目策略（[[tables/ca_fee_project_config]]）——以及 `cafee` 代码包。

**同义词**：CA服务费、CA收费、CA证书服务费在本域内可互换使用。

**易混边界**：本概念与 **CFCA认证**、**CA认证**、**电子签章**有关联但属于不同功能域——后者面向证书/签章能力的开通与认证，前者面向"收费"。企业台账上的 `ca_status`（签章状态）来自签章中台，是跨域引用字段，不代表本域的缴费结论。使用本词时若讨论的是"能不能用证书"，请改指认证域；若是"要不要交钱、交了没有"，才落在本页。

据此，本域的判定链是：项目是否收费 → 企业角色是否收费 → 是否豁免 → 是否已缴 → 场景是否拦截，分别见[[rules/rule_engine_priority]]、[[rules/chargeable_company_role_rule]]、[[rules/multi_project_exemption_rule]]、[[rules/intercept_scene_rule]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），本页术语边界来自代码与库表证据的语义桥接。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

---END FILE---

---FILE: concepts/unified_social_credit_code.md ---
---
type: concept
title: 统码
page_key: concepts/unified_social_credit_code
domain: CA证书收费
status: draft
aliases: [统一社会信用代码, certification_no]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - db:ca_fee_order
contract_version: "0.1"
maps_to: ca_fee_company.certification_no、ca_fee_order.certification_no
field_targets:
  - ca_fee_company.certification_no
  - ca_fee_order.certification_no
adjudication: synonym
also_confused_with: [企业ID, companyId]
---

# 统码

## 业务定位

**统码**即统一社会信用代码，是 CA 收费域内企业的**唯一标识**，用于关联企业主数据。库表字段名为 `certification_no`，出现在[[tables/ca_fee_company]]（企业台账）与[[tables/ca_fee_order]]（订单）两侧，是两表对齐同一家企业的业务键。

**同义词**：统一社会信用代码、`certification_no`。

**易混边界**：统码 ≠ **企业ID / companyId**。统码是工商登记口径的、全局唯一的社会信用代码；`companyId` 是产融平台内部的企业主键 ID。二者可能同时出现在同一业务流程中，但**不可互相替代**做关联或去重——引用企业时应显式说明使用的是哪一个。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自库表字段语义。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

---END FILE---

---FILE: concepts/core_enterprise.md ---
---
type: concept
title: 核企
page_key: concepts/core_enterprise
domain: CA证书收费
status: draft
aliases: [核心企业, CORE]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - db:ca_fee_order
  - code:CaFeePaymentCheckApplication.java
contract_version: "0.1"
maps_to: company_type / source_company_type = 'CORE'
field_targets:
  - ca_fee_company.source_company_type
  - ca_fee_order.company_type
adjudication: synonym
also_confused_with: []
---

# 核企

## 业务定位

**核企**（核心企业）在 CA 收费场景下是**可收费角色之一**，在[[tables/ca_fee_company]]中以 `source_company_type='CORE'` 表示首次锁定时的来源角色，在[[tables/ca_fee_order]]中以 `company_type='CORE'` 表示订单归属角色。其年费标准取项目配置的 `core_annual_fee`（见[[tables/ca_fee_project_config]]）。

**同义词**：核心企业、`CORE`。

角色是否参与收费校验见[[rules/chargeable_company_role_rule]]与口径[[calibers/chargeable_company_role]]；与之并列的另一可收费角色见[[concepts/supplier]]。企业角色中还可能出现 `PROJECT_COMPANY`，本页不对其是否收费做断言——收费对象仅由规则页给出。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自库表字段与代码枚举。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

---END FILE---

---FILE: concepts/supplier.md ---
---
type: concept
title: 供应商
page_key: concepts/supplier
domain: CA证书收费
status: draft
aliases: [SUPPLIER]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - db:ca_fee_order
  - code:CaFeePaymentCheckApplication.java
contract_version: "0.1"
maps_to: company_type / source_company_type = 'SUPPLIER'
field_targets:
  - ca_fee_company.source_company_type
  - ca_fee_order.company_type
adjudication: synonym
also_confused_with: []
---

# 供应商

## 业务定位

**供应商**在 CA 收费场景下是**可收费角色之一**，在[[tables/ca_fee_company]]中以 `source_company_type='SUPPLIER'` 记录首次锁定的来源角色，在[[tables/ca_fee_order]]中以 `company_type='SUPPLIER'` 记录订单归属角色。其年费标准取项目配置的 `supplier_annual_fee`（见[[tables/ca_fee_project_config]]）。

**同义词**：`SUPPLIER`。

是否参与收费校验见[[rules/chargeable_company_role_rule]]与口径[[calibers/chargeable_company_role]]；与核企（[[concepts/core_enterprise]]）的区别仅在角色取值与年费标准来源，均为本域可收费对象。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自库表字段与代码枚举。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

---END FILE---

---FILE: concepts/bocom.md ---
---
type: concept
title: 交e保
page_key: concepts/bocom
domain: CA证书收费
status: draft
aliases: [BOCOM]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeePaymentApplication.java
contract_version: "0.1"
maps_to: ca_fee_order.pay_method = 'BOCOM'
field_targets:
  - ca_fee_order.pay_method
  - ca_fee_order.bocom_txn_sts
adjudication: synonym
also_confused_with: [银行转账]
---

# 交e保

## 业务定位

**交e保**是当前 CA 服务费的**唯一支付渠道**（对公打款），在[[tables/ca_fee_order]]中以 `pay_method='BOCOM'` 标识。围绕它的关键字段包括：交易状态 `bocom_txn_sts`、平台流水号 `bocom_plfm_ser_no`、平台业务编号 `bocom_plfm_bsn_id`、请求流水号 `bocom_req_sn`。

**同义词**：`BOCOM`。

**易混边界**：交e保 ≠ **银行转账**。二者虽同为对公付款，但交e保走平台化接口与流水号回执，业务上需要按交易状态判成功/失败/待查证——对应口径[[calibers/bocom_success]]（`00`）、[[calibers/bocom_failure]]（`01`）、[[calibers/bocom_pending_investigation]]（`02`）。**待查证（02）不等于失败**，不可直接并入失败口径。

支付发起的前置条件见[[rules/payment_precondition_rule]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自库表字段与代码枚举。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

---END FILE---

---FILE: concepts/todo.md ---
---
type: concept
title: 待办
page_key: concepts/todo
domain: CA证书收费
status: draft
aliases: [todo, notice, 提醒]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeMessageGateway.java
contract_version: "0.1"
maps_to: CaFeeMessageGateway.sendTodoForOrder / completeNoticeForOrder
field_targets: []
adjudication: synonym
also_confused_with: [站内信, 邮件]
---

# 待办

## 业务定位

**待办**指 CA 服务费场景下通过消息网关发送的**通知任务**，覆盖缴费、续费、到期等节点，由 `CaFeeMessageGateway` 的 `sendTodoForOrder` 下发、`completeNoticeForOrder` 完结。它是业务动作（提请缴费、催续费、告知到期）在系统内的可追踪载体。

**同义词**：`todo`、`notice`、`提醒`。

**易混边界**：待办 ≠ **站内信**、≠ **邮件**。后两者是**送达渠道**，待办是**业务任务语义**；同一待办可以经不同渠道触达，讨论时请区分"发了什么待办"与"用什么通道发"。

待办生成与复位的状态标记见[[tables/ca_fee_company]]的 `renew_remind_sent` 及状态机[[processes/ca_fee_renew_remind]]；触发条件见[[rules/renew_remind_rule]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自代码调用点。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

---END FILE---

---FILE: calibers/paid_company.md ---
---
type: caliber
title: 已缴费企业
page_key: calibers/paid_company
domain: CA证书收费
status: draft
aliases: [PAID 企业, pay_status=PAID]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 已缴费企业

## 业务定位

以[[tables/ca_fee_company]]的 `pay_status='PAID'` 判定。用于统计"当前无欠费"的企业规模。注意该口径为**企业维度的状态快照**，不保证订单侧存在对应的已支付单据（见[[calibers/paid_order]]），两者不可互相替代。其对偶口径见[[calibers/unpaid_company]]。

状态如何从 `PAID` 变为 `UNPAID` 见[[processes/ca_fee_company_pay_status]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表字段取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 已缴费企业
predicate: "ca_fee_company.pay_status = 'PAID'"
scope: ca_fee_company
evidence: db
```

---END FILE---

---FILE: calibers/unpaid_company.md ---
---
type: caliber
title: 未缴费企业
page_key: calibers/unpaid_company
domain: CA证书收费
status: draft
aliases: [UNPAID 企业, pay_status=UNPAID]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 未缴费企业

## 业务定位

以[[tables/ca_fee_company]]的 `pay_status='UNPAID'` 判定，是本域**欠费/待缴**的基准口径。服务到期处理会把企业置为 `UNPAID`（见[[processes/ca_fee_company_pay_status]]），因此该口径同时包含"从未缴费"与"已到期未续费"两类企业；**若业务只想看前者，需叠加服务期口径**（[[calibers/service_expired]]、[[calibers/in_service_period]]）进一步区分。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表字段取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 未缴费企业
predicate: "ca_fee_company.pay_status = 'UNPAID'"
scope: ca_fee_company
evidence: db
```

---END FILE---

---FILE: calibers/agreement_signed_order.md ---
---
type: caliber
title: 已签署协议订单
page_key: calibers/agreement_signed_order
domain: CA证书收费
status: draft
aliases: [agreement_signed=Y, 协议已签订单]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 已签署协议订单

## 业务定位

以[[tables/ca_fee_order]]的 `agreement_signed='Y'` 判定。该口径是**支付准入的前置条件之一**，与订单状态共同约束支付发起（见[[rules/payment_precondition_rule]]）。签署动作与版本号、签署时间、协议文件路径一并记录，签署状态自身的流转见[[processes/ca_fee_agreement_sign]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表字段取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 已签署协议订单
predicate: "ca_fee_order.agreement_signed = 'Y'"
scope: ca_fee_order
evidence: db
```

---END FILE---

---FILE: calibers/pending_order.md ---
---
type: caliber
title: 待支付订单
page_key: calibers/pending_order
domain: CA证书收费
status: draft
aliases: [PENDING 订单, order_status=PENDING]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 待支付订单

## 业务定位

以[[tables/ca_fee_order]]的 `order_status='PENDING'` 判定，是"未缴费且仍可发起支付"的订单集合。这是支付准入状态，也是续费、催缴类统计的基口径。

注意库中存在 `PAIDING`、`UNPAID` 等**代码枚举之外的取值**（见[[processes/ca_fee_order_state]]），本口径仅覆盖 `PENDING`，不覆盖这些值；若需要"全部未支付"的口径，须另行评审定义。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码枚举。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 待支付订单
predicate: "ca_fee_order.order_status = 'PENDING'"
scope: ca_fee_order
evidence: code
```

---END FILE---

---FILE: calibers/paid_order.md ---
---
type: caliber
title: 已支付订单
page_key: calibers/paid_order
domain: CA证书收费
status: draft
aliases: [PAID 订单, order_status=PAID]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 已支付订单

## 业务定位

以[[tables/ca_fee_order]]的 `order_status='PAID'` 判定，用于收入/缴费笔数统计。支付成功由交e保划扣成功后回写（见[[processes/ca_fee_order_state]]与[[rules/payment_precondition_rule]]）。

与[[calibers/paid_company]]的区别：本口径是**单据级**、反映历史交易；后者是**企业级当前状态**，会因服务到期而回退为 `UNPAID`。二者在同一时点不一定一致，跨期比对时需声明口径。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码枚举。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 已支付订单
predicate: "ca_fee_order.order_status = 'PAID'"
scope: ca_fee_order
evidence: code
```

---END FILE---

---FILE: calibers/enabled_company.md ---
---
type: caliber
title: 有效企业
page_key: calibers/enabled_company
domain: CA证书收费
status: draft
aliases: [enable=Y, 逻辑有效企业]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 有效企业

## 业务定位

以[[tables/ca_fee_company]]的 `enable='Y'` 判定，是**逻辑启用**过滤条件。任何统计或业务判定在遍历企业台账前都应先叠加本口径，避免把已失效记录计入。它是**过滤条件**而非业务状态，与服务期（[[calibers/in_service_period]]）、缴费状态（[[calibers/paid_company]]）正交，需要组合使用。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 有效企业
predicate: "ca_fee_company.enable = 'Y'"
scope: ca_fee_company
evidence: code
```

---END FILE---

---FILE: calibers/charge_enabled_project.md ---
---
type: caliber
title: 收费项目
page_key: calibers/charge_enabled_project
domain: CA证书收费
status: draft
aliases: [charge_enabled=Y, 已开启收费项目]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_project_config
contract_version: "0.1"
---

# 收费项目

## 业务定位

以[[tables/ca_fee_project_config]]的 `charge_enabled='Y'` 判定，表示该项目已开启 CA 收费。它是[[rules/rule_engine_priority|规则引擎优先级]]的**第一道闸**：项目未开启收费即整体放行，不进入后续豁免与金额判定。业务上回答"这个项目到底收不收 CA 服务费"。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 收费项目
predicate: "ca_fee_project_config.charge_enabled = 'Y'"
scope: ca_fee_project_config
evidence: code
```

---END FILE---

---FILE: calibers/chargeable_company_role.md ---
---
type: caliber
title: 核企/供应商角色
page_key: calibers/chargeable_company_role
domain: CA证书收费
status: draft
aliases: [source_company_type in CORE,SUPPLIER, 可收费角色]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 核企/供应商角色

## 业务定位

以[[tables/ca_fee_company]]的 `source_company_type` 是否落在 `('CORE','SUPPLIER')` 判定，用于圈定**可收费角色**。该口径与[[rules/chargeable_company_role_rule|收费对象规则]]一一对应：仅这两类角色需要校验 CA 服务费，其他角色（如 `PROJECT_COMPANY`）直接放行。

角色术语含义见[[concepts/core_enterprise]]与[[concepts/supplier]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 核企/供应商角色
predicate: "ca_fee_company.source_company_type in ('CORE','SUPPLIER')"
scope: ca_fee_company
evidence: code
```

---END FILE---

---FILE: calibers/in_service_period.md ---
---
type: caliber
title: 服务期内
page_key: calibers/in_service_period
domain: CA证书收费
status: draft
aliases: [service_end >= 今日, 服务有效期覆盖今日]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 服务期内

## 业务定位

以[[tables/ca_fee_company]]的 `service_end >= CURDATE()` 判定，表示企业当前 CA 服务周期**覆盖当日**（服务截止日含当日）。这是"该企业现在是否还享有 CA 服务"的判据，与缴费状态（[[calibers/paid_company]]）相互独立：未缴费企业也可能仍在服务期内（享受已购周期）。

三个时间口径互斥且应成套使用：[[calibers/in_service_period]]（未到期）、[[calibers/expiring_soon]]（≤7 天将到期）、[[calibers/service_expired]]（已到期）。边界日为**含当日**，跨口径拼接时注意不要在 7 天窗口上重复计数。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 服务期内
predicate: "ca_fee_company.service_end >= CURDATE()"
scope: ca_fee_company
evidence: code
```

---END FILE---

---FILE: calibers/expiring_soon.md ---
---
type: caliber
title: 即将到期
page_key: calibers/expiring_soon
domain: CA证书收费
status: draft
aliases: [7天内到期, renew_remind_sent=N 待提醒]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 即将到期

## 业务定位

以[[tables/ca_fee_company]]的 `service_end <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)` **且** `renew_remind_sent='N'` 判定，即"7 天内到期且本期续费待办尚未生成"。它同时是[[rules/renew_remind_rule|续费提醒规则]]的触发条件与续费待办生成的工作队列口径。

**使用注意**：本口径内含 `renew_remind_sent='N'`，只适用于"待推送提醒"的场景；若业务想统计"所有 7 天内到期的企业"（不论是否已提醒），需去掉后半个条件另行定义。提醒生成后该企业即退出本口径，状态流转见[[processes/ca_fee_renew_remind]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 即将到期
predicate: "ca_fee_company.service_end <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND ca_fee_company.renew_remind_sent = 'N'"
scope: ca_fee_company
evidence: code
```

---END FILE---

---FILE: calibers/service_expired.md ---
---
type: caliber
title: 服务已到期
page_key: calibers/service_expired
domain: CA证书收费
status: draft
aliases: [service_end < 今日, 已过期服务]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 服务已到期

## 业务定位

以[[tables/ca_fee_company]]的 `service_end < CURDATE()` 判定，表示服务周期已过截止日（因服务截止日含当日，`service_end = 今日` 仍属[[calibers/in_service_period]]）。与[[calibers/in_service_period]]严格互补，与[[calibers/expiring_soon]]在 7 天窗口上存在语义重叠（本口径只看已过期，不看到期前的提醒窗口）。

服务到期处理会关闭 RENEW 待缴单并将企业置为 `UNPAID`（见[[processes/ca_fee_company_pay_status]]与[[rules/renew_remind_rule]]）。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 服务已到期
predicate: "ca_fee_company.service_end < CURDATE()"
scope: ca_fee_company
evidence: code
```

---END FILE---

---FILE: calibers/whitelist_exempt.md ---
---
type: caliber
title: 白名单豁免
page_key: calibers/whitelist_exempt
domain: CA证书收费
status: draft
aliases: [EXEMPT_WHITELIST, 特殊配置且年费为0]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 白名单豁免

## 业务定位

以[[tables/ca_fee_company]]的 `special_config_flag='Y'` 且 `special_annual_fee=0` 判定：企业存在生效中的特殊配置快照，且特殊配置后应缴年费为 0。命中即视为**免缴**，在[[rules/multi_project_exemption_rule|多项目豁免规则]]与[[rules/rule_engine_priority|规则引擎优先级]]中按 `EXEMPT_WHITELIST` 放行。

与[[calibers/targeted_reduction]]的差别仅在 `special_annual_fee` 是否为 0：为 0 是豁免，大于 0 是减免，二者共用 `special_config_flag='Y'` 这一前置。特殊配置来源见[[tables/ca_fee_project_config]]的 `special_company_list`。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 白名单豁免
predicate: "ca_fee_company.special_config_flag = 'Y' AND ca_fee_company.special_annual_fee = 0"
scope: ca_fee_company
evidence: code
```

---END FILE---

---FILE: calibers/targeted_reduction.md ---
---
type: caliber
title: 定向减免
page_key: calibers/targeted_reduction
domain: CA证书收费
status: draft
aliases: [特殊年费大于0, 定向减免企业]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 定向减免

## 业务定位

以[[tables/ca_fee_company]]的 `special_config_flag='Y'` 且 `special_annual_fee > 0` 判定：企业存在生效中的特殊配置快照，且特殊年费不为 0——即**仍需缴费但金额被定向调整**（通常低于项目标准价）。

该值在[[rules/annual_fee_pricing_rule|年费定价规则]]中享有**最高优先级**：特殊年费 → 已锁定年费 → 项目角色价。因此命中本口径的企业，其订单 `annual_fee` 不会再回落到 `locked_annual_fee` 或项目价。

与[[calibers/whitelist_exempt]]的区别仅在于 `special_annual_fee` 是否为 0，请勿混用。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 定向减免
predicate: "ca_fee_company.special_config_flag = 'Y' AND ca_fee_company.special_annual_fee > 0"
scope: ca_fee_company
evidence: code
```

---END FILE---

---FILE: calibers/bocom_success.md ---
---
type: caliber
title: 交e保划扣成功
page_key: calibers/bocom_success
domain: CA证书收费
status: draft
aliases: [bocom_txn_sts=00, 划扣成功]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 交e保划扣成功

## 业务定位

以[[tables/ca_fee_order]]的 `bocom_txn_sts='00'` 判定，表示交e保（[[concepts/bocom]]）渠道划扣成功。该口径是**支付结果的最底层凭据**，订单转 `PAID` 以其为依据（见[[processes/ca_fee_order_state]]）。

三个交易状态口径须成套使用：[[calibers/bocom_success]]（`00`）、[[calibers/bocom_failure]]（`01`）、[[calibers/bocom_pending_investigation]]（`02`）；`02` 属于结果未定，**不得并入成功或失败**。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 交e保划扣成功
predicate: "ca_fee_order.bocom_txn_sts = '00'"
scope: ca_fee_order
evidence: db
```

---END FILE---

---FILE: calibers/bocom_pending_investigation.md ---
---
type: caliber
title: 交e保划扣待查证
page_key: calibers/bocom_pending_investigation
domain: CA证书收费
status: draft
aliases: [bocom_txn_sts=02, 划扣待查证]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 交e保划扣待查证

## 业务定位

以[[tables/ca_fee_order]]的 `bocom_txn_sts='02'` 判定，表示交e保（[[concepts/bocom]]）侧**划扣结果尚未确定**，需要人工或后续对账查证。这是一类独立的中间态：既不能计入[[calibers/bocom_success]]，也不能计入[[calibers/bocom_failure]]。

对账场景下本口径是**待处理工作队列**；在收入统计中则应单列，避免资金口径错报。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 交e保划扣待查证
predicate: "ca_fee_order.bocom_txn_sts = '02'"
scope: ca_fee_order
evidence: code
```

---END FILE---

---FILE: calibers/bocom_failure.md ---
---
type: caliber
title: 交e保划扣失败
page_key: calibers/bocom_failure
domain: CA证书收费
status: draft
aliases: [bocom_txn_sts=01, 划扣失败]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 交e保划扣失败

## 业务定位

以[[tables/ca_fee_order]]的 `bocom_txn_sts='01'` 判定，表示交e保（[[concepts/bocom]]）渠道划扣失败。该口径用于失败率与重试分析，**不应**被计入[[calibers/bocom_success]]；同时注意与[[calibers/bocom_pending_investigation]]（`02` 待查证）区分，后者结果未定。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 交e保划扣失败
predicate: "ca_fee_order.bocom_txn_sts = '01'"
scope: ca_fee_order
evidence: code
```

---END FILE---

---FILE: rules/chargeable_company_role_rule.md ---
---
type: rule
title: 收费对象规则
page_key: rules/chargeable_company_role_rule
domain: CA证书收费
status: draft
aliases: [收费角色规则, isChargeableCompanyRole]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeePaymentCheckApplication.java:checkFeePaymentForPortal:isChargeableCompanyRole
contract_version: "0.1"
---

# 收费对象规则

## 业务定位

**只有核心企业（CORE）与供应商（SUPPLIER）两类角色需要校验 CA 服务费**；其他企业角色直接放行，不进入拦截流程。这条规则决定了门户缴费校验的**入口边界**——非可收费角色根本不会走到金额与豁免判定。

角色术语见[[concepts/core_enterprise]]、[[concepts/supplier]]，对应口径[[calibers/chargeable_company_role]]。通过本规则后，才轮到[[rules/rule_engine_priority|规则引擎优先级]]与[[rules/intercept_scene_rule|拦截场景规则]]决定是否真正阻断。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

决定门户缴费校验是否拦截：非 CORE/SUPPLIER 角色一律放行。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 收费对象规则
content: 仅核心企业（CORE）和供应商（SUPPLIER）角色需要校验CA服务费；其他企业角色直接放行，不拦截。
impact: 决定门户缴费校验是否拦截。
field_targets: [ca_fee_company.source_company_type, ca_fee_order.company_type]
evidence: "code_path:CaFeePaymentCheckApplication.java:checkFeePaymentForPortal:isChargeableCompanyRole"
```

---END FILE---

---FILE: rules/multi_project_exemption_rule.md ---
---
type: rule
title: 多项目豁免规则
page_key: rules/multi_project_exemption_rule
domain: CA证书收费
status: draft
aliases: [shouldPassByEvaluate, 多项目放行规则]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeePaymentCheckApplication.java:shouldPassByEvaluate
contract_version: "0.1"
---

# 多项目豁免规则

## 业务定位

当企业关联**多个收费项目**时，按关联时间**升序**遍历项目：任一项目命中**白名单豁免（EXEMPT_WHITELIST）**、**延期支付豁免（EXEMPT_DEFER_PAY）**或**服务期内已缴费（EXEMPT_ALREADY_PAID）**，则整体放行（`pass=true`）。

这是一条**"从宽"**规则：只要有一个项目可豁免，就不拦截该企业。因此多项目企业的拦截结论**不取决于当前访问的项目**，而取决于其全部关联项目的豁免情况——排查拦截问题时应遍历全部关联项目，而非只看当前项目。

相关口径：[[calibers/whitelist_exempt]]、[[calibers/in_service_period]]、[[calibers/paid_company]]；字段来源[[tables/ca_fee_company]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

多项目企业只要有一个豁免项目即不拦截。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 多项目豁免规则
content: 企业关联多个收费项目时，按关联时间升序遍历项目，任一项目命中白名单豁免（EXEMPT_WHITELIST）、延期支付豁免（EXEMPT_DEFER_PAY）或服务期内已缴费（EXEMPT_ALREADY_PAID），则整体放行（pass=true）。
impact: 多项目企业只要有一个豁免项目即不拦截。
field_targets: [ca_fee_company.special_config_flag, ca_fee_company.special_annual_fee, ca_fee_company.service_end]
evidence: "code_path:CaFeePaymentCheckApplication.java:shouldPassByEvaluate"
```

---END FILE---

---FILE: rules/intercept_scene_rule.md ---
---
type: rule
title: 拦截场景规则
page_key: rules/intercept_scene_rule
domain: CA证书收费
status: draft
aliases: [block_scene_list 规则, doCheckFeePayment]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeePaymentCheckApplication.java:doCheckFeePayment
contract_version: "0.1"
---

# 拦截场景规则

## 业务定位

**需缴费且需要拦截时，只有当前请求的 `interceptScene` 命中项目配置的 `block_scene_list` 才真正拦截；否则放行**。

这条规则把"企业欠费"与"此刻是否阻断业务"解耦：欠费企业可以照常使用未被列入拦截场景的功能。项目侧的配置载体见[[tables/ca_fee_project_config]]。

排查"为什么欠费却没被拦"时，应先确认该项目 `block_scene_list` 是否包含当前场景，再确认[[rules/chargeable_company_role_rule|收费对象规则]]与[[rules/multi_project_exemption_rule|多项目豁免规则]]的结论。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

决定业务节点是否被阻断。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 拦截场景规则
content: 需缴费时，仅当项目配置的 block_scene_list 包含当前请求的 interceptScene 才拦截；否则放行。
impact: 决定业务节点是否被阻断。
field_targets: [ca_fee_project_config.block_scene_list]
evidence: "code_path:CaFeePaymentCheckApplication.java:doCheckFeePayment"
```

---END FILE---

---FILE: rules/annual_fee_pricing_rule.md ---
---
type: rule
title: 年费定价规则
page_key: rules/annual_fee_pricing_rule
domain: CA证书收费
status: draft
aliases: [resolveAnnualFee, 应缴年费取值规则]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeRuleEngineService.java:resolveAnnualFee
contract_version: "0.1"
---

# 年费定价规则

## 业务定位

应缴年费按**优先级**解析：① 生效中的特殊年费（`special_annual_fee`）→ ② 已锁定的年费（`locked_annual_fee`）→ ③ 项目角色价（`core_annual_fee` / `supplier_annual_fee`）。结果落在订单 `annual_fee`。

业务含义：**特殊配置优先于历史锁定价，历史锁定价优先于项目当前标准价**。因此项目调价不会影响已锁定企业，而特殊配置企业则以特殊价为准（豁免情形见[[calibers/whitelist_exempt]]，减免情形见[[calibers/targeted_reduction]]）。字段来源：[[tables/ca_fee_company]]、[[tables/ca_fee_project_config]]；落点[[tables/ca_fee_order]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

决定订单 annual_fee。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 年费定价规则
content: 应缴年费按优先级：生效中的特殊年费（special_annual_fee）→ 已锁定的年费（locked_annual_fee）→ 项目角色价（core_annual_fee / supplier_annual_fee）。
impact: 决定订单 annual_fee。
field_targets: [ca_fee_company.special_annual_fee, ca_fee_company.locked_annual_fee, ca_fee_project_config.core_annual_fee, ca_fee_project_config.supplier_annual_fee]
evidence: "code_path:CaFeeRuleEngineService.java:resolveAnnualFee"
```

---END FILE---

---FILE: rules/rule_engine_priority.md ---
---
type: rule
title: 规则引擎优先级
page_key: rules/rule_engine_priority
domain: CA证书收费
status: draft
aliases: [evaluate 判定顺序, 缴费判定优先级]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeRuleEngineService.java:evaluate
contract_version: "0.1"
---

# 规则引擎优先级

## 业务定位

评估企业是否需要缴费的**判定顺序**为：

1. 项目未开启收费 → 放行；
2. 白名单豁免 → 放行；
3. 延期支付 → 放行；
4. 服务期内已缴费 → 放行；
5. 应缴金额为 0 → 放行；
6. 其余 → 需缴费（`UNPAID`/`EXPIRED`）。

顺序即优先级：**前序条件命中即短路**，不再进入后续判断。因此"金额为 0"这一条排在豁免之后，仅对未被前四类豁免覆盖的企业生效。结果产出 `feeStatus` 与 `needPay`，业务侧据此决定是否进入[[rules/intercept_scene_rule|拦截场景规则]]。

相关口径：[[calibers/charge_enabled_project]]、[[calibers/whitelist_exempt]]、[[calibers/in_service_period]]、[[calibers/paid_company]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

决定 feeStatus 和 needPay。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 规则引擎优先级
content: 评估企业是否需要缴费的优先级：项目未开启收费 → 白名单豁免 → 延期支付 → 服务期内已缴费 → 应缴金额为0 → 需缴费（UNPAID/EXPIRED）。
impact: 决定 feeStatus 和 needPay。
field_targets: [ca_fee_order, ca_fee_company]
evidence: "code_path:CaFeeRuleEngineService.java:evaluate"
```

---END FILE---

---FILE: rules/payment_precondition_rule.md ---
---
type: rule
title: 支付前置条件规则
page_key: rules/payment_precondition_rule
domain: CA证书收费
status: draft
aliases: [requirePendingSignedOrder, confirmBocomPaid, 支付准入规则]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeePaymentApplication.java:requirePendingSignedOrder,confirmBocomPaid
contract_version: "0.1"
---

# 支付前置条件规则

## 业务定位

发起支付必须同时满足：**订单处于 `PENDING`**（[[calibers/pending_order]]）且**已签署收费协议 `agreement_signed='Y'`**（[[calibers/agreement_signed_order]]）。支付方式固定为交e保（`BOCOM`，见[[concepts/bocom]]）；划扣成功后把订单标记为 `PAID`。

两个条件缺一不可：未签协议不能付款，已支付/已关闭订单不能重复支付。协议签署状态流转见[[processes/ca_fee_agreement_sign]]，订单状态流转见[[processes/ca_fee_order_state]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

约束支付流程。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 支付前置条件规则
content: 订单必须处于 PENDING 且 agreement_signed='Y' 才能发起支付；支付方式为交e保（BOCOM）；划扣成功后标记订单为 PAID。
impact: 约束支付流程。
field_targets: [ca_fee_order.order_status, ca_fee_order.agreement_signed, ca_fee_order.pay_method]
evidence: "code_path:CaFeePaymentApplication.java:requirePendingSignedOrder,confirmBocomPaid"
```

---END FILE---

---FILE: rules/renew_remind_rule.md ---
---
type: rule
title: 续费提醒规则
page_key: rules/renew_remind_rule
domain: CA证书收费
status: draft
aliases: [caFeeRenewalTodoJob, 续费待办规则]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeScheduledJobHandler.java:caFeeRenewalTodoJob
contract_version: "0.1"
---

# 续费提醒规则

## 业务定位

企业 `service_end` 距今 **≤7 天** 且 `renew_remind_sent='N'` 时：生成 **RENEW 待缴订单**并发送续费待办，随后把 `renew_remind_sent` 置为 `'Y'`。

这是一条**定时任务驱动**的规则（`caFeeRenewalTodoJob`），服务期临近截止时自动触发续费动作。`renew_remind_sent` 起到幂等闸的作用，保证同一周期只生成一次；该标记在服务到期处理时会被复位，见[[processes/ca_fee_renew_remind]]。触发集合口径见[[calibers/expiring_soon]]，待办术语见[[concepts/todo]]，字段见[[tables/ca_fee_company]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

触发续费订单和提醒。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 续费提醒规则
content: 企业 service_end 距今 ≤7 天且 renew_remind_sent='N' 时，生成 RENEW 待缴订单并发送续费待办，随后置 renew_remind_sent='Y'。
impact: 触发续费订单和提醒。
field_targets: [ca_fee_company.service_end, ca_fee_company.renew_remind_sent]
evidence: "code_path:CaFeeScheduledJobHandler.java:caFeeRenewalTodoJob"
```

---END FILE---

---REVIEW: rule | 服务到期规则---
语义分析中「服务到期规则」的条目在传输中被**截断**：`content` 取值止于「按需创建 RENEW_EXPIRED 」，`evidence` 字段完全缺失（条目在 JSON 中被切断）。

- 已知（可作为上下文、但不构成锚点）：内容涉及 `service_end < 当日` 时完结即将到期待办、关闭 RENEW 待缴单、将企业 `pay_status` 置为 `UNPAID`；与状态机 [[processes/ca_fee_order_state]] 中的 `processServiceExpired`、[[processes/ca_fee_company_pay_status]] 的 `markServiceExpired`、[[processes/ca_fee_renew_remind]] 的复位动作可相互印证。
- 缺失：完整的 `content` 结尾（"按需创建 RENEW_EXPIRED …" 之后的条件与动作）、`impact`、`field_targets`、`evidence` 代码路径。

未生成 `rules/service_expired_rule.md`，以免在锚点块中写入非逐字、可能被发明的内容。请补充该规则的完整条目（尤其 `evidence` 的 `code_path:文件:方法`）后重新触发本页生成。
---END REVIEW---

---REVIEW: meta | 物理库名（scope.databases）---
本次语义分析的 `field_semantics` / `state_machines` / `calibers` 仅以 `[DB]`、`[代码]` 标注证据来源，**未给出任何物理库名（database/schema）**。因此全部 36 个页面的 frontmatter `scope.databases` 统一写为占位符 `["<物理库名>"]`，未做任何猜测性填写。

- 待确认：承载 `ca_fee_company` / `ca_fee_order` / `ca_fee_project_config` 的物理库名（若涉及多库或分库，请给出完整清单）。
- 影响：`ground:columns` 等锚点块中的 `evidence: db` 目前无法回溯到具体库实例；补齐库名后可提升锚点可核验性。
---END REVIEW---