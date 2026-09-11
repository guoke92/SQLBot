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