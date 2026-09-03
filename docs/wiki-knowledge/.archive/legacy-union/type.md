---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-status-operations@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 生命周期操作类型
page_key: type
domain: 客户与建档
aliases:
- 冻结记录
- 解冻记录
anchors:
- type
---
# 生命周期操作类型

cust_company_lifecycle_info.type 记录操作类型。

```ground:enum
enum: type
fields:
- cust_company_lifecycle_info.type
values:
  FRZ:
    label: 冻结
  UNFRZ:
    label: 解冻
```

## 关联
- [[cust_company_lifecycle_info|cust_company_lifecycle_info]]
