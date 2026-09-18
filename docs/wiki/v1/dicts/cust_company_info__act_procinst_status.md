---
type: dict
title: cust_company_info.act_procinst_status
page_key: cust_company_info__act_procinst_status
belong: dicts
status: draft
anchors: [cust_company_info.act_procinst_status]
sources: ['database_profile:cust_company_info.act_procinst_status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.act_procinst_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_company_info.act_procinst_status`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__act_procinst_status
fields: [cust_company_info.act_procinst_status]
values:
  待客户确认: {trust: proposed}
  认证失败: {trust: proposed}
  退回: {trust: proposed}
  审批中: {trust: proposed}
  变更成功: {trust: proposed}
triage: keep
```
