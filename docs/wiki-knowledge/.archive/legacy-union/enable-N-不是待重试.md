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
title: enable=N 不是待重试
page_key: enable-N-不是待重试
domain: openapi
field_targets:
- client_api_sync_error.enable
---
# enable=N 不是待重试

当前库中 client_api_sync_error 全部 enable=N，不能解释为待重试失败。

```ground:rule
rule: sync-error-enable-n-not-retry
field_targets:
- client_api_sync_error.enable
impact: query_constraint
content: 当前库中 client_api_sync_error 全部 enable=N，不能解释为待重试失败。
scope: 同步失败、待重试
```

## 关联
- [[client_api_sync_error]]
