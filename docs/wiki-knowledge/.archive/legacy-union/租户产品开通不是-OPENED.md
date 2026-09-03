---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:tenant-product-lifecycle@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 租户产品开通不是 OPENED
page_key: 租户产品开通不是-OPENED
domain: product
field_targets:
- tenant_product.open_status
---
# 租户产品开通不是 OPENED

tenant_product.open_status 只用 Y/P/N。企业申请表的 OPENED/OPENING/NOT_OPENED 属于另一单元。

```ground:rule
rule: tenant-product-open-is-ynp
field_targets:
- tenant_product.open_status
impact: query_constraint
content: tenant_product.open_status 只用 Y/P/N。企业申请表的 OPENED/OPENING/NOT_OPENED 属于另一单元。
scope: 已开通产品、开通中产品
```

## 关联
- [[tenant_product]]
