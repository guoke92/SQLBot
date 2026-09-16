---
type: caliber
title: 对外可见资方规则
page_key: active_funding_rule
domain: 资金规则与异常处理
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - funding_rule_info.rule_status
  - funding_rule_info.enable
---

规则提供方只查 ACTIVE。

```ground:caliber
name: 对外可见资方规则
predicate: "funding_rule_info.rule_status = 'ACTIVE' AND funding_rule_info.enable = 'Y'"
scope: funding_rule_info
evidence: code
```
