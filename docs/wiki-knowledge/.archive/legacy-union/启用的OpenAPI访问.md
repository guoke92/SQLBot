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
type: caliber
title: 启用的OpenAPI访问
page_key: 启用的OpenAPI访问
domain: openapi
field_targets:
- cust_access_secret.enable
---
# 启用的OpenAPI访问

enable=Y 的记录。

```ground:caliber
caliber: 启用的OpenAPI访问
field_targets:
- cust_access_secret.enable
filters:
- .cust_access_secret.enable = 'Y'
```

## 关联
- [[cust_access_secret]]
