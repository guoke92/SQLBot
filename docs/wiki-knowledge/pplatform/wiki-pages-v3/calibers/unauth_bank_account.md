---
type: caliber
title: 未打款认证账户
page_key: unauth_bank_account
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
  - cust_account_info.auth_state
---

打款认证仍为初始化。

```ground:caliber
name: 未打款认证账户
predicate: "cust_account_info.auth_state = 'APPLY_00'"
scope: cust_account_info
evidence: code
```
