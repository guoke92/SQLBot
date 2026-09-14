---
type: rule
title: 年费定价链规则
page_key: annual_fee_pricing_chain
domain: CA证书收费
status: draft
aliases:
  - 定价链
  - resolveAnnualFee
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: rules
---

应缴年费按优先级解析：`special_annual_fee` → `locked_annual_fee`（仅当 `fee_locked=Y`）→ 项目角色价 `core_annual_fee`／`supplier_annual_fee`；角色价解析为 0 元时视同豁免（对多项目放行与豁免判定产生影响）。相关口径见 [[company_fee_locked]]、[[company_special_config_flag]]。

## 需求背景

同一企业可能同时存在特殊定价、锁定价与项目角色价，必须固定优先级才能保证订单金额可复现；锁定价的存在是为了让首次缴费成功后的价格不随项目调价而变。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 年费定价链规则
content: 应缴年费按 special_annual_fee -> locked_annual_fee（fee_locked=Y） -> 项目角色价 core_annual_fee/supplier_annual_fee 解析；角色价0元时视同豁免
impact: 决定订单 annual_fee 和是否需缴费
field_targets:
  - ca_fee_company.special_annual_fee
  - ca_fee_company.locked_annual_fee
  - ca_fee_company.fee_locked
  - ca_fee_project_config.core_annual_fee
  - ca_fee_project_config.supplier_annual_fee
evidence: CaFeeRuleEngineService.resolveAnnualFee
```