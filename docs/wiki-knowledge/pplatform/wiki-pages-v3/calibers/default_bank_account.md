---
type: caliber
title: 默认银行账户
page_key: default_bank_account
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
  - cust_account_info.default_account_flag
---

同一企业默认账户互斥，代码只保留一个 `'1'`。

```ground:caliber
name: 默认银行账户
predicate: "cust_account_info.default_account_flag = '1' AND cust_account_info.enable = 'Y'"
scope: cust_account_info
evidence: code
```
