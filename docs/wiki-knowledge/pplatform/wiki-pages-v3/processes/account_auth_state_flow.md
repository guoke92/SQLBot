---
type: process
title: 账户打款认证状态机
page_key: account_auth_state_flow
domain: 企业银行账户/集团/SFTP
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - cust_account_info.auth_state
---

小额打款认证。库内绝大多数停在 APPLY_00。

```ground:process
name: 账户打款认证状态机
field: cust_account_info.auth_state
states:
  - value: APPLY_00
    label: 初始化
    source: code_enum
  - value: APPLY_10
    label: 申请受理中
    source: code_enum
  - value: APPLY_20
    label: 受理打款成功
    source: code_enum
  - value: APPLY_30
    label: 受理打款失败
    source: code_enum
  - value: APPLY_40
    label: 成功
    source: code_enum
  - value: APPLY_50
    label: 失败
    source: code_enum
transitions:
  - from: APPLY_00
    event: 发起打款申请
    to: APPLY_10
    evidence: "code_path:CustAccountApplication.java:190"
  - from: APPLY_10
    event: 打款成功
    to: APPLY_20
    evidence: "code_path:CustAccountApplication.java:224"
  - from: APPLY_10
    event: 打款失败
    to: APPLY_30
    evidence: "code_path:CustAccountApplication.java:228"
  - from: APPLY_20
    event: 验证成功
    to: APPLY_40
    evidence: "code_path:CustAccountApplication.java:278"
  - from: APPLY_20
    event: 验证失败
    to: APPLY_50
    evidence: "code_path:CustAccountApplication.java:289"
```
