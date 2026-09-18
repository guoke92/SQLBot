---
type: dict
title: cust_invite_info.db_tenant_code
page_key: cust_invite_info__db_tenant_code
belong: dicts
status: draft
anchors: [cust_invite_info.db_tenant_code]
sources: ['database_profile:cust_invite_info.db_tenant_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_invite_info]
---

# cust_invite_info.db_tenant_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `cust_invite_info.db_tenant_code`，表页 [[tables/cust_invite_info]]。

## 取值

```ground:dict
dict: cust_invite_info__db_tenant_code
fields: [cust_invite_info.db_tenant_code]
values:
  beehive-scf.qhhrly.cn: {trust: proposed}
  LN1: {trust: proposed}
  jiuersanzuhu: {trust: proposed}
  LN2: {trust: proposed}
  ISOLATE_TAG_hscc: {trust: proposed}
  ning: {trust: proposed}
triage: hold
needs_review: true
```
