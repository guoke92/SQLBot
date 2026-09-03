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
type: enum
title: 启用异常建议
page_key: enable
domain: funding
aliases:
- 有效建议
anchors:
- enable
---
# 启用异常建议

enable=Y 的异常解析记录才参与查询与导出。

```ground:enum
enum: enable
fields:
- funding_exception_resolution.enable
values:
  Y:
    label: 启用
```

## 关联
- [[funding_exception_resolution|funding_exception_resolution]]
