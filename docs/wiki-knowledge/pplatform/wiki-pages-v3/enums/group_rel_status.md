---
type: enum
title: group_rel_status
page_key: group_rel_status
domain: 企业银行账户/集团/SFTP
status: draft
aliases: [已生效成员]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [group_rel_status_flow]
---

# group_rel_status

`CustGroupRelStatusEnum`。列注释同步：已生效 EFFECTIVE / 未生效 INEFFECTIVE / 已拒绝 REJECTED。

```ground:enum
enum: group_rel_status
fields:
  - cust_group_rel.status
values:
  "INEFFECTIVE":
    label: "未生效"
  "EFFECTIVE":
    label: "已生效"
  "REJECTED":
    label: "已拒绝"
```
