---
type: dict
title: cust_certification_info.manual_verify_status
page_key: cust_certification_info__manual_verify_status
belong: dicts
status: draft
anchors: [cust_certification_info.manual_verify_status]
sources: ['database_profile:cust_certification_info.manual_verify_status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_certification_info]
---

# cust_certification_info.manual_verify_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_certification_info.manual_verify_status`，表页 [[tables/cust_certification_info]]。

## 取值

```ground:dict
dict: cust_certification_info__manual_verify_status
fields: [cust_certification_info.manual_verify_status]
values:
  MANUAL_AUTHENTICATION_PASSED: {trust: proposed}
triage: keep
```
