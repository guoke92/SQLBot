---
type: caliber
title: 已激活企业角色
page_key: effective_role
domain: 客户角色与端口
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - cust_role_info.status
  - cust_role_info.enable
---

企业已激活的角色切片。

```ground:caliber
name: 已激活企业角色
predicate: "cust_role_info.status = 'EFFECT' AND cust_role_info.enable = 'Y'"
scope: cust_role_info
evidence: code
```
