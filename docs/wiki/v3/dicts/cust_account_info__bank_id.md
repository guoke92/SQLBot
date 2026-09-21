---
type: dict
title: cust_account_info.bank_id
page_key: cust_account_info__bank_id
belong: dicts
status: draft
anchors: [cust_account_info.bank_id]
sources: ['database_profile:cust_account_info.bank_id']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_account_info]
---

# cust_account_info.bank_id

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_account_info.bank_id`，表页 [[tables/cust_account_info]]。

## 取值

```ground:dict
dict: cust_account_info__bank_id
fields: [cust_account_info.bank_id]
values:
  '103': {trust: proposed}
  '302': {trust: proposed}
  '102': {trust: proposed}
  '105': {trust: proposed}
triage: hold
needs_review: true
```
