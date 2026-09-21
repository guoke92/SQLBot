---
type: rule
title: 异常建议不是规则头
page_key: exception_not_rule_head
belong: rules
domain: funding_rule
status: draft
field_targets: [funding_exception_resolution.error_keyword]
sources: ['code_path:ExceptionResolutionApplication.java:524']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [funding_exception_resolution]
---

# 异常建议不是规则头

异常表无 rule_info_id。不要用它判断规则是否 ACTIVE。

```ground:rule
rule: 异常建议不是规则头
field_targets: [funding_exception_resolution.error_keyword]
impact: query_constraint
content: 异常表无 rule_info_id。不要用它判断规则是否 ACTIVE。
evidence: code_path:ExceptionResolutionApplication.java:524
```

## 页面链接

- [[tables/funding_exception_resolution]]
