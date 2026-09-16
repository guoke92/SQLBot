---
type: caliber
title: 集团根企业
page_key: group_root
domain: 企业银行账户/集团/SFTP
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
  - cust_group_rel.root_flag
---

是否集团企业列为 Y。

```ground:caliber
name: 集团根企业
predicate: "cust_group_rel.root_flag = 'Y'"
scope: cust_group_rel
evidence: code
```
