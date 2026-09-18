---
type: dict
title: cust_head_company_info.enable
page_key: cust_head_company_info__enable
belong: dicts
status: draft
anchors: [cust_head_company_info.enable]
sources: ['database_profile:cust_head_company_info.enable']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_head_company_info]
---

# cust_head_company_info.enable

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `cust_head_company_info.enable`，表页 [[tables/cust_head_company_info]]。

## 取值

```ground:dict
dict: cust_head_company_info__enable
fields: [cust_head_company_info.enable]
values:
  Y: {trust: proposed}
triage: hold
needs_review: true
```
