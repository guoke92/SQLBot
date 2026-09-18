---
type: dict
title: ca_fee_company.ca_status
page_key: ca_fee_company__ca_status
belong: dicts
status: draft
anchors: [ca_fee_company.ca_status]
sources: ['database_profile:ca_fee_company.ca_status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [ca_fee_company]
---

# ca_fee_company.ca_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `ca_fee_company.ca_status`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__ca_status
fields: [ca_fee_company.ca_status]
values:
  NORMAL: {trust: proposed}
  CANCELLED: {trust: proposed}
  UNKNOWN: {trust: proposed}
triage: keep
```
