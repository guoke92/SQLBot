---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-product-activation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 变更单状态
page_key: status
domain: 客户与建档
aliases:
- 变更审核
- 在途变更
- 变更通过
- 变更拒绝
- 变更单
- 变更流程
- 企业变更
anchors:
- status
---
# 变更单状态

cust_change_record.status 与企业 check_status 共用 CheckStatus 六值； 在途判定 = status IS NULL OR NOT IN (CUST_CHECK_PASS, CUST_CHECK_REJECT)。

```ground:enum
enum: status
fields:
- cust_change_record.status
values:
  CUST_CHECK_INIT:
    label: 待审核
  CUST_CHECK_CHECKING:
    label: 审核中
  CUST_CHECK_PASS:
    label: 审核通过
  CUST_CHECK_REJECT:
    label: 审核不通过
  CUST_CHECK_BACKTOCUSTOM:
    label: 待客户确认
  CUST_BACK:
    label: 退回
```

## 关联
- [[cust_change_record|cust_change_record]]
