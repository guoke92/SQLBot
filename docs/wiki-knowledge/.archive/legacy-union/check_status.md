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
title: 审核状态
page_key: check_status
domain: 客户与建档
aliases:
- 审核通过
- 审核拒绝
- 审核不通过
- 待审核
- 退回客户
anchors:
- check_status
---
# 审核状态

运营中台工作流审核状态（回调写入）：CUST_CHECK_PASS 审核通过时联动写 cust_build_status=BUILD_SUCCESS 与 cust_status=EFFECT。

```ground:enum
enum: check_status
fields:
- cust_company_info.check_status
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
- [[cust_company_info|cust_company_info]]
