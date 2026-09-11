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