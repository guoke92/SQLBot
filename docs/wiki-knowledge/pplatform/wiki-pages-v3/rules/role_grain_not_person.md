---
type: rule
title: 企业角色行不是联系人
page_key: role_grain_not_person
domain: 客户角色与端口
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - cust_role_info.role_type
  - cust_person_info.company_type
---

cust_role_info 一企一角色一行；联系人是人绑在角色切片上。数「有多少供应商企业」用角色或企业主档，不要数联系人行。

```ground:rule
name: 企业角色行不是联系人
content: cust_role_info 一企一角色一行；联系人是人绑在角色切片上。数「有多少供应商企业」用角色或企业主档，不要数联系人行。
field_targets: [cust_role_info.role_type, cust_person_info.company_type]
evidence: "code_path:CustRoleApplication.java:64"
```
