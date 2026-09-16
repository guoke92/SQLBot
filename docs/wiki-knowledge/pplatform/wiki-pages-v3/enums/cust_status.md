---
type: enum
title: cust_status
page_key: cust_status
domain: 企业建档与认证状态机
status: draft
aliases: [企业状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [cust_status_flow]
---

# cust_status

[[cust_company_info]] 的 `cust_status`：企业本身状态。`CustStatusEnum`。流转见 [[cust_status_flow]]。

与 [[cust_build_status]]（认证过程）不是同一列。有效企业口径见 [[effective_company]]（`EFFECT` + `enable='Y'`）。`FAILURE` 在枚举中，本表库分布未见。

```ground:enum
enum: cust_status
fields: [cust_company_info.cust_status]
values:
  "ADD":
    label: "新增"
  "EFFECT":
    label: "生效"
  "FAILURE":
    label: "失效"
  "WRITEOFF":
    label: "注销"
  "FREEZE":
    label: "冻结"
  "CHANGE":
    label: "变更"
```
