---
type: dict
title: cust_change_record.status
page_key: cust_change_record__status
belong: dicts
status: draft
anchors: [cust_change_record.status]
sources: ['database_profile:cust_change_record.status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_change_record.status`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__status
fields: [cust_change_record.status]
values:
  CUST_CHECK_PASS: {trust: proposed}
  CUST_CHECK_REJECT: {trust: proposed}
  CUST_CHECK_CHECKING: {trust: proposed}
  '1': {trust: proposed}
  CUST_CHECK_BACKTOCUSTOM: {trust: proposed}
  returnCust-2026-07-03 10:24: {trust: proposed}
  returnCust-2026-07-15 17:30: {trust: proposed}
  returnCust-2026-07-22 14:55: {trust: proposed}
  CUSTS003: {trust: proposed}
  returnCust-2024-07-17 10:10: {trust: proposed}
  returnCust-2024-09-10 14:10: {trust: proposed}
  returnCust-2024-11-01 14:16: {trust: proposed}
  returnCust-2024-11-05 10:03: {trust: proposed}
  returnCust-2024-11-12 10:05: {trust: proposed}
  returnCust-2025-01-17 14:38: {trust: proposed}
  returnCust-2025-07-22 12:03: {trust: proposed}
  returnCust-2026-05-25 14:55: {trust: proposed}
  returnCust-2026-05-22 20:22: {trust: proposed}
triage: keep
```
