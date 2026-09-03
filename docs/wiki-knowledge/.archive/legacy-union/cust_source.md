---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-build-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 建档数据来源
page_key: cust_source
domain: 客户与建档
aliases:
- 存量迁移企业
- 中台推送企业
- 产融自建企业
anchors:
- cust_source
---
# 建档数据来源

企业建档数据的系统级来源。

```ground:enum
enum: cust_source
fields:
- cust_company_info.cust_source
values:
  PLATFORM_PUSH:
    label: 运营中台推送
  MIGRATORY:
    label: 存量迁移企业
  PPLATFORM:
    label: 产融自建企业
```

## 关联
- [[cust_company_info|cust_company_info]]
