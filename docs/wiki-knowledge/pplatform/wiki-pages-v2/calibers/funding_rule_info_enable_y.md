---
type: caliber
title: 资方规则有效数据口径
page_key: funding_rule_info_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方规则 enable 口径
  - funding_rule_info enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
contract_version: "0.1"
belong: calibers
---

[[funding_rule_info]] 的导出查询以 enable='Y' 为口径，saveRuleInfo 新增时固定写 'Y'。

## 需求背景

本口径与状态口径叠加使用：导出看 enable，对外 Provider 看 ruleStatus=ACTIVE（[[rule_provider_active_only]]），两者不可互相替代——规则可能 enable='Y' 但处于 PENDING / INACTIVE（[[funding_rule_status_machine]]）。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 资方规则有效数据
predicate: funding_rule_info.enable = 'Y'
scope: 导出查询过滤；saveRuleInfo 新增固定写 Y
evidence: code
```