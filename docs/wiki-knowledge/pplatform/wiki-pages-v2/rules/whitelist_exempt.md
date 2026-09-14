---
type: rule
title: 白名单豁免规则
page_key: whitelist_exempt
domain: CA证书收费
status: draft
aliases:
  - WHITELIST 豁免
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: rules
---

企业快照 `special_config_flag=Y` 且 `special_annual_fee=0`，并与项目 `special_company_list` 中**生效的** `WHITELIST` 交叉校验后，`needPay=false`，`exemptReason=WHITELIST`，服务期截止取零元豁免特殊值。相关口径见 [[company_special_config_flag]]，术语边界见 [[whitelist]]，服务期语义见 [[service_period]]。

## 需求背景

白名单企业免缴 CA 服务费，但配置源在项目侧、判定在规则引擎侧，因此必须交叉校验，避免快照过期导致误免。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 白名单豁免规则
content: 企业快照 special_config_flag=Y 且 special_annual_fee=0，并与项目 special_company_list 中生效 WHITELIST 交叉校验后，needPay=false，exemptReason=WHITELIST，服务期截止取零元豁免特殊值
impact: 白名单企业免缴CA服务费
field_targets:
  - ca_fee_company.special_config_flag
  - ca_fee_company.special_annual_fee
  - ca_fee_project_config.special_company_list
evidence: CaFeeRuleEngineService.isWhitelistExempt
```