---
type: caliber
title: 规则层枚举（DB 实测）
page_key: funding_rule_detail_rule_layer_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - rule_layer 分布
  - 规则层级分布
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_detail
contract_version: "0.1"
belong: calibers
---

[[funding_rule_detail]].rule_layer 的实测取值分布以 FINANCING 为主，UNDERLYING 次之，OTHER 最少。

## 需求背景

该分布印证了 Provider 对外按 ruleLayer 聚合成「底层（UNDERLYING）/融资（FINANCING）/其他（OTHER）」三组的必要性（[[rule_provider_active_only]]）。层级值在保存时由 [[funding_rule_front_cfg]].rule_layer 复制而来，见 [[rule_layer]]。

## 版本演进

v0 首次建立，计数取自 calibers 条目 DB 证据。

```ground:caliber
name: 规则层枚举（DB 实测）
predicate: funding_rule_detail.rule_layer = 'FINANCING'
scope: DB 925/1530；UNDERLYING 499、OTHER 106
evidence: db
```