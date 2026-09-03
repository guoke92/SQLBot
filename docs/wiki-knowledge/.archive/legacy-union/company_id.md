---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-auxiliary@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 企业生命周期
page_key: company_id
domain: 企业建档
aliases:
- 冻结企业
- 解冻企业
anchors:
- company_id
---
# 企业生命周期

cust_company_lifecycle_info 以 type 记录冻结或解冻事件；enable 表示记录是否启用。

```ground:enum
enum: company_id
fields:
- cust_company_lifecycle_info.company_id
- cust_company_lifecycle_info.type
- cust_company_lifecycle_info.enable
values:
  FRZ:
    label: 冻结
  UNFRZ:
    label: 解冻
  Y:
    label: 启用
  N:
    label: 停用
```

## 关联
- [[cust_company_lifecycle_info|cust_company_lifecycle_info]]
