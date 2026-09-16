---
type: enum
title: rule_status
page_key: rule_status
domain: 资金规则与异常处理
status: draft
aliases: [生效中规则]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [rule_status_flow]
---

# rule_status

`RuleStatusEnum`。

```ground:enum
enum: rule_status
fields:
  - funding_rule_info.rule_status
values:
  "PENDING":
    label: "待生效"
  "ACTIVE":
    label: "生效中"
  "INACTIVE":
    label: "已失效"
```
