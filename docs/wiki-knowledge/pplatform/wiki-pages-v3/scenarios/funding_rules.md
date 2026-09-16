---
type: scenario
title: 资金规则
page_key: funding_rules
domain: 资金规则与异常处理
status: draft
aliases: [资方规则, 异常关键字]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:资金规则与异常处理"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [funding_rule_info]
field_targets:
  - funding_rule_info.rule_status
---

# 资金规则

问「生效中的资方规则 / 异常关键字怎么解析」时进入本场景。

**主档** [[funding_rule_info]]。明细 [[funding_rule_detail]] 用 `rule_info_id` 等值关联。异常 [[funding_exception_resolution]] 按产品+资方+关键字；对外查询要求 `enable='Y'`。前端配置 `funding_rule_front_cfg` 靠 `rule_key=front_key` 在应用里配对，不是 SQL 外键。

```ground:scenario
scenario: funding_rules
hubs:
- table: funding_rule_info
  role: master
  grain: 一条资方规则头
  window:
  - id
  - enable
  - create_time
  - update_time
  - rule_status
  - funding_party_mark
  - product_code
  - version
- table: funding_rule_detail
  role: detail
  grain: 一条规则明细
  window:
  - id
  - enable
  - create_time
  - update_time
  - rule_info_id
  - rule_layer
- table: funding_exception_resolution
  role: exception
  grain: 一条异常关键字
  window:
  - id
  - enable
  - create_time
  - update_time
  - product_code
  - funding_party_code
  - error_keyword
lifecycle:
- enum: rule_status
  process: rule_status_flow
shared: []
```
