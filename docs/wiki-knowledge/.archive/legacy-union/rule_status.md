---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:funding-party-rules@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 规则状态
page_key: rule_status
domain: 资金方规则
aliases:
- 待生效规则
- 生效中规则
- 已失效规则
- 规则状态机
anchors:
- rule_status
---
# 规则状态

funding_rule_info.rule_status 三值状态机：PENDING 待生效（新建默认）→ ACTIVE 生效中（activeRule 人工激活）→ INACTIVE 已失效（inActiveRule 停用）。更新规则不新建主行只 version+1，rule_status 不随更新重置。

```ground:enum
enum: rule_status
fields:
- funding_rule_info.rule_status
values:
  PENDING:
    label: 待生效
  ACTIVE:
    label: 生效中
  INACTIVE:
    label: 已失效
```

## 关联
- [[funding_rule_info|funding_rule_info]]
