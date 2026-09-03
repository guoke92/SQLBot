---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:exception-resolution@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某个资金方报错关键字的建议是什么
page_key: list-exception-by-keyword
domain: funding
anchors:
- funding_exception_resolution
---
# 某个资金方报错关键字的建议是什么

问法：某个资金方报错关键字的建议是什么

```ground:pattern
pattern: list-exception-by-keyword
question: 某个资金方报错关键字的建议是什么
sql: SELECT error_keyword, error_reason, suggestion FROM funding_exception_resolution
  WHERE funding_party_code = ? AND error_keyword = ? AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[funding_exception_resolution]]
