---
type: caliber
title: 有效集团成员
page_key: effective_group_member
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
  - cust_group_rel.status
---

成员列表接口只返回已生效。

```ground:caliber
name: 有效集团成员
predicate: "cust_group_rel.status = 'EFFECTIVE'"
scope: cust_group_rel
evidence: code
```
