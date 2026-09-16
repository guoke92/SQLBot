---
type: enum
title: account_auth_state
page_key: account_auth_state
domain: 企业银行账户/集团/SFTP
status: draft
aliases: [打款认证]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [account_auth_state_flow]
---

# account_auth_state

`AccountAuthState`。库分布几乎全是 APPLY_00。

```ground:enum
enum: account_auth_state
fields:
  - cust_account_info.auth_state
values:
  "APPLY_00":
    label: "初始化"
  "APPLY_10":
    label: "申请受理中"
  "APPLY_20":
    label: "受理打款成功"
  "APPLY_30":
    label: "受理打款失败"
  "APPLY_40":
    label: "成功"
  "APPLY_50":
    label: "失败"
```
