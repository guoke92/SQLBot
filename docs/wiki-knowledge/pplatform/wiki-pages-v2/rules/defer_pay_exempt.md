---
type: rule
title: 延期支付豁免规则
page_key: defer_pay_exempt
domain: CA证书收费
status: draft
aliases:
  - DEFER_PAY 豁免
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: rules
---

在**无生效定向减免**的前提下，若项目 `special_company_list` 中存在 `DEFER_PAY` 且 `today <= deferServiceEnd`，则 `needPay=false`，`exemptReason=DEFER_PAY`。批量写入延期名单的运营动作见 [[batch_whitelist_defer]]。

## 需求背景

部分企业需要延期缴纳（非免除），需要在延期到期前不产生缴费拦截，同时保留到期后恢复收费的能力；因此以服务结束日作为延期窗口边界。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 延期支付豁免规则
content: 无生效定向减免时，项目 special_company_list 中存在 DEFER_PAY 且 today<=deferServiceEnd，则 needPay=false，exemptReason=DEFER_PAY
impact: 延期企业暂不缴费
field_targets:
  - ca_fee_project_config.special_company_list
evidence: CaFeeRuleEngineService.resolveDeferPay
```