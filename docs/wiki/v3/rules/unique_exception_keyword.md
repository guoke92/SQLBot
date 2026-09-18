---
type: rule
title: 同一产品同一资金方报错关键字不重复
page_key: unique_exception_keyword
belong: rules
domain: funding_rule
status: draft
field_targets: [funding_exception_resolution.product_code, funding_exception_resolution.funding_party_code,
  funding_exception_resolution.error_keyword]
sources: ['code_path:ExceptionResolutionApplication.java:524']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_exception_resolution]
---

# 同一产品同一资金方报错关键字不重复

保存异常建议时按产品+资金方+关键字查重。

```ground:rule
rule: 同一产品同一资金方报错关键字不重复
field_targets: [funding_exception_resolution.product_code, funding_exception_resolution.funding_party_code,
  funding_exception_resolution.error_keyword]
impact: write_constraint
content: 保存异常建议时按产品+资金方+关键字查重。
evidence: code_path:ExceptionResolutionApplication.java:524
```

## 页面链接

- [[tables/funding_exception_resolution]]
- [[dicts/funding_exception_resolution__funding_party_code]]
- [[dicts/funding_exception_resolution__product_code]]
