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
title: 有效 OpenAPI 渠道
page_key: 有效-OpenAPI-渠道
domain: openapi
field_targets:
- cust_access_secret.channel
- cust_access_secret.enable
---
# 有效 OpenAPI 渠道

渠道配置存在且 enable=Y；请求 channel 必须命中该配置。

```ground:caliber
caliber: 有效 OpenAPI 渠道
field_targets:
- cust_access_secret.channel
- cust_access_secret.enable
filters:
- .access_secret.enable = 'Y'
- .access_secret.channel = '<请求channel>'
```

## 关联
- [[cust_access_secret]]
