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