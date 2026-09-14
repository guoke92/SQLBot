---
type: caliber
title: 前端规则配置有效数据口径
page_key: funding_rule_front_cfg_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - frontCfg enable 口径
  - funding_rule_front_cfg enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
contract_version: "0.1"
belong: calibers
---

[[funding_rule_front_cfg]] 的有效性口径同时作用于导入校验（按 (product, rule_layer, key_name) 反查 frontKey）与 Provider 查询。

## 需求背景

导入与保存都依赖本口径拿到可用字段集合；若配置被置为非 'Y'，则该字段无法被导入解析，保存时 ruleMap 中多余的 frontKey 会被静默跳过（[[rule_save_version_detail_sync]]）。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 前端规则配置有效数据
predicate: funding_rule_front_cfg.enable = 'Y'
scope: 导入校验与 Provider 查询过滤
evidence: code
```