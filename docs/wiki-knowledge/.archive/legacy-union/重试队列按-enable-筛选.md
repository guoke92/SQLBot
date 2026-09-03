---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:openapi-access@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 重试队列按 enable 筛选
page_key: 重试队列按-enable-筛选
domain: openapi
field_targets:
- client_api_sync_error.enable
---
# 重试队列按 enable 筛选

重试扫描只取 enable=Y；处理时若记录已变为 N 则跳过。

```ground:rule
rule: retry-queue-enable-filter
field_targets:
- client_api_sync_error.enable
impact: query_constraint
content: 重试扫描只取 enable=Y；处理时若记录已变为 N 则跳过。
scope: 同步失败重试
```

## 关联
- [[client_api_sync_error]]
