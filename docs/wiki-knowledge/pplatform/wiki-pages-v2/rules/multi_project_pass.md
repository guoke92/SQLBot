---
type: rule
title: 多项目放行规则
page_key: multi_project_pass
domain: CA证书收费
status: draft
aliases:
  - 多项目放行
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentCheckApplication.java
contract_version: "0.1"
belong: rules
---

多项目企业遍历所有**已开启收费**的项目分别调用 `evaluate`，只要任一命中白名单、0 元特殊定价、延期豁免或服务期内已缴费，即 `pass=true` 放行。该规则决定企业级缴费校验的最终结论，是各单项豁免规则的**聚合出口**（见 [[whitelist_exempt]]、[[defer_pay_exempt]]、[[already_paid_in_service]]、[[annual_fee_pricing_chain]]）。

## 需求背景

同一企业可能在多个项目下存在角色，若采用「任一项未缴即拦截」的口径，会导致企业因单个未开放或已豁免的项目被误拦；因此采用「任一放行即放行」的宽松聚合。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 多项目放行规则
content: 多项目企业遍历所有已开启收费项目 evaluate，任一命中白名单、0元特殊定价、延期豁免或服务期内已缴费，即 pass=true 放行
impact: 企业有多个项目时避免因单个项目未缴被拦截
field_targets:
  - ca_fee_project_config.charge_enabled
  - ca_fee_company.pay_status
  - ca_fee_company.special_config_flag
evidence: CaFeePaymentCheckApplication.doCheckFeePayment
```