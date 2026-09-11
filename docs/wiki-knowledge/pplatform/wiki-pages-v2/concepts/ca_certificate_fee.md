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