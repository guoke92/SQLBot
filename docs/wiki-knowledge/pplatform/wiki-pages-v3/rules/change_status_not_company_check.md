---
type: rule
title: 变更单状态不是企业准入审核
page_key: change_status_not_company_check
domain: 企业变更与运营变更
status: draft
aliases: [CheckStatus 两列]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:OperApiConstants.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - cust_change_record.status
  - cust_company_info.check_status
---

`CheckStatus` 同一套值写在两列上：变更单看 [[cust_change_record]].status，企业准入看 [[cust_company_info]].check_status。企业是否变更中看 [[cust_status]]=`CHANGE`。

```ground:rule
name: 变更单状态不是企业准入审核
content: 同名字典 CheckStatus 绑两列；问变更审核过滤变更单 status，问企业准入过滤 check_status，问变更中企业过滤 cust_status=CHANGE。
impact: 混列会导致用变更单去数企业，或把准入审核当成变更进度。
field_targets: [cust_change_record.status, cust_company_info.check_status]
evidence: "code_path:OperApiConstants.java:CheckStatus"
```
