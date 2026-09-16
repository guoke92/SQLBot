---
type: process
title: 资方规则状态机
page_key: rule_status_flow
domain: 资金规则与异常处理
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - funding_rule_info.rule_status
---

新建 PENDING，activeRule → ACTIVE，inActiveRule → INACTIVE，可再激活。

```ground:process
name: 资方规则状态机
field: funding_rule_info.rule_status
states:
  - value: PENDING
    label: 待生效
    source: code_enum
  - value: ACTIVE
    label: 生效中
    source: code_enum
  - value: INACTIVE
    label: 已失效
    source: code_enum
transitions:
  - from: PENDING
    event: 规则生效
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:287"
  - from: ACTIVE
    event: 规则失效
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:314"
  - from: INACTIVE
    event: 再次生效
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java:287"
```
