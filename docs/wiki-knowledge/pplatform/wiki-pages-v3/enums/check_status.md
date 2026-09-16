---
type: enum
title: check_status
page_key: check_status
domain: 企业变更与运营变更
status: draft
aliases: [审核状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:OperApiConstants.CheckStatus", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [cust_change_record_status]
---

# check_status

`OperApiConstants.CheckStatus`，`.name()` 落库。绑两列：

- [[cust_change_record]].status — 变更单审核，流转见 [[cust_change_record_status]]
- [[cust_company_info]].check_status — 企业准入审核（与建档 [[cust_build_status]]、企业 [[cust_status]] 都不是同一列）

label 用构造函数中文。`CUST_BACK` 在枚举中；变更单库分布另有 `'1'`、`CUSTS003`、`returnCust-时间戳`，企业 `check_status` 另有 1 条 `EFFECT`，均无代码声明。

```ground:enum
enum: check_status
fields: [cust_change_record.status, cust_company_info.check_status]
values:
  "CUST_CHECK_INIT":
    label: "待审核"
  "CUST_CHECK_CHECKING":
    label: "审核中"
  "CUST_CHECK_PASS":
    label: "审核通过"
  "CUST_CHECK_REJECT":
    label: "审核不通过"
  "CUST_CHECK_BACKTOCUSTOM":
    label: "待客户确认"
  "CUST_BACK":
    label: "退回"
  "1":
    note: "变更单库中 377 条；代码枚举未声明"
  "EFFECT":
    note: "企业 check_status 库中 1 条；属 cust_status 取值"
```
