---
type: caliber
title: 审核中的变更单
page_key: pending_change
domain: 企业变更与运营变更
status: draft
aliases: [变更审核中]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:cust_change_record"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets: [cust_change_record.status]
---

列在 [[cust_change_record]]。不是 [[in_change_company]]。

```ground:caliber
name: 审核中的变更单
predicate: "cust_change_record.status = 'CUST_CHECK_CHECKING'"
scope: cust_change_record
evidence: db
```
