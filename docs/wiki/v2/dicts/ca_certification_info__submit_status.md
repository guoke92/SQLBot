---
type: dict
title: ca_certification_info.submit_status
page_key: ca_certification_info__submit_status
belong: dicts
status: draft
anchors: [ca_certification_info.submit_status]
sources: ['database_profile:ca_certification_info.submit_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [ca_certification_info]
---

# ca_certification_info.submit_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `ca_certification_info.submit_status`，表页 [[tables/ca_certification_info]]。

## 取值

```ground:dict
dict: ca_certification_info__submit_status
fields: [ca_certification_info.submit_status]
values:
  SUCCESS: {trust: proposed}
  PENDING: {trust: proposed}
  FAIL: {trust: proposed}
triage: keep
```
