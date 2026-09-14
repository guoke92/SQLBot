---
type: concept
title: CA服务费
page_key: ca_service_fee
domain: CA证书收费
status: draft
aliases:
  - CA证书收费
  - CA收费
  - 电子认证服务费
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeController.java + reqdoc:ca-fee-mvp-phase1-20260625
  - code_path:CaFeePaymentCheckApplication.java + reqdoc:ca-fee-mvp-phase1-20260625
  - code_path:CaFeeRuleEngineService.java + reqdoc:ca-fee-mvp-phase1-20260625
contract_version: "0.1"
maps_to: ca_fee_order.annual_fee
field_targets:
  - ca_fee_order.annual_fee
adjudication: boundary
boundary: 费用金额字段是 annual_fee；ca_status 是证书状态，不是收费金额
also_confused_with:
  - ca_fee_company.ca_status
belong: concepts
field_targets: [ca_fee_order.annual_fee]
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实)：CA证书收费需求由产品经理张彬伟（Vincent）负责。

「CA服务费」指对使用电子认证服务（CA 证书）的用户开通的收费模式，在数据上落到**费用金额**字段：订单侧的 `ca_fee_order.annual_fee`（应缴年费）与其实际缴纳结果 `pay_amount`。它与管理对象 `ca_fee_company`、配置源 `ca_fee_project_config` 共同构成「项目—订单—企业」三层。

**边界（易混淆）**：`ca_service_fee` 与 [[ca_status_normal]] 等 CA 状态不是一回事——`ca_status` 描述证书是否有效，`annual_fee` 描述要收多少钱。讨论「CA 收费」时若引用了 `ca_fee_company.ca_status`，应校正到费用字段。

## 需求背景

CA 证书收费是产融平台 V1.32 版本推出的全新商业模式／产品功能点，对使用电子认证服务（CA 证书）的用户开通收费模式。这一主张在代码侧有落点：`CaFeeController`（入口）、`CaFeePaymentCheckApplication`（缴费校验）、`CaFeeRuleEngineService`（收费规则引擎），并与需求文档 `CA服务费MVP版本（一期）需求文档-20260625` 对应；该外部文档未内联具体收费规则、计费页面与维护流程，故本主题的规则与页面契约以代码与库表证据为准。

## 版本演进

- v0（本页）：建立术语桥与边界；记录 V1.32 全新商业模式的主张来源（代码 + 需求文档双源）。
- (document_claim，未证实)：CA证书收费需求由产品经理张彬伟（Vincent）负责——代码侧无对应证据，仅作需求侧归属记录。

相关：[[ca_fee_order]]
