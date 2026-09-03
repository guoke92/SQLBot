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
title: 冻结企业
page_key: cust_status
domain: 客户与建档
aliases:
- 冻结
- 解冻
- 企业生命周期操作
anchors:
- cust_status
---
# 冻结企业

cust_status=FREEZE 的企业；每次冻结/解冻在 cust_company_lifecycle_info 落一条 台账（type=FRZ/UNFRZ，确认后 enable=Y）。

```ground:enum
enum: cust_status
fields:
- cust_company_info.cust_status
values:
  FREEZE:
    label: 冻结
  EFFECT:
    label: 生效
  WRITEOFF:
    label: 注销
```

## 关联
- [[cust_company_info|cust_company_info]]
