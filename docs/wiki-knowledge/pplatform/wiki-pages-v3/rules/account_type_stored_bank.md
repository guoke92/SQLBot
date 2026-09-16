---
type: rule
title: 银行账户库值是 BANK
page_key: account_type_stored_bank
domain: 企业银行账户/集团/SFTP
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
  - cust_account_info.account_type
---

枚举 dictKey `'1'`=银行，写入路径存枚举名 BANK。按 `'1'` 过滤会漏掉主存量。

```ground:rule
name: 银行账户库值是 BANK
content: 枚举 dictKey `'1'`=银行，写入路径存枚举名 BANK。按 `'1'` 过滤会漏掉主存量。
field_targets: [cust_account_info.account_type]
evidence: "code_path:CustPersonController.java:305"
```
