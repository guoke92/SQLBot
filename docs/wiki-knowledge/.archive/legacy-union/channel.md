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
type: enum
title: 有效渠道接入密钥
page_key: channel
domain: openapi
aliases:
- OpenAPI 密钥
- 启用渠道
anchors:
- channel
---
# 有效渠道接入密钥

cust_access_secret 中 channel 匹配请求且 enable=Y 的渠道配置；密钥原文不作为问数口径。

```ground:enum
enum: channel
fields:
- cust_access_secret.channel
- cust_access_secret.enable
values:
  Y:
    label: 启用
  N:
    label: 停用
```

## 关联
- [[cust_access_secret|cust_access_secret]]
