---
type: process
title: 变更单审核状态机
page_key: cust_change_record_status
domain: 企业变更与运营变更
status: draft
aliases: [变更审核]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustCompanyInfoApplication.java", "code:CustChangeApplication.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [cust_change_record.status]
---

作用于 [[cust_change_record]] 的 `status`（字典 [[check_status]]）。不要当成企业 [[cust_company_info]].check_status 的状态机。

```ground:process
name: 企业变更记录审核状态
field: cust_change_record.status
states:
  - value: CUST_CHECK_INIT
    label: 待审核
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 待客户确认
    source: code_enum
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核不通过
    source: code_enum
transitions:
  - from: CUST_CHECK_INIT
    event: 发起变更同步运营中台
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustCompanyInfoApplication.java:submitCust"
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核退回
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: "code_path:CustCompanyInfoApplication.java:syncClientForSimple"
  - from: CUST_CHECK_CHECKING
    event: 流程重建 changeRebuild
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustChangeApplication.java:changeRebuild"
```
