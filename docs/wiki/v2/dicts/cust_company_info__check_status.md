---
type: dict
title: cust_company_info.check_status
page_key: cust_company_info__check_status
belong: dicts
status: draft
anchors: [cust_company_info.check_status]
sources: ['database_profile:cust_company_info.check_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.check_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_company_info.check_status`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__check_status
fields: [cust_company_info.check_status]
values:
  CUST_CHECK_PASS: {trust: proposed}
  CUST_CHECK_BACKTOCUSTOM: {trust: proposed}
  CUST_CHECK_REJECT: {trust: proposed}
  CUST_CHECK_CHECKING: {trust: proposed}
  CUST_CHECK_INIT: {trust: proposed}
  EFFECT: {trust: proposed}
triage: keep
```
