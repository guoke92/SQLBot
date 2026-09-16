---
type: process
title: 集团关系状态机
page_key: group_rel_status_flow
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
  - cust_group_rel.status
---

新成员 INEFFECTIVE；根企业建档成功或成员接受 → EFFECTIVE；拒绝 → REJECTED。

```ground:process
name: 集团关系状态机
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效
    source: code_enum
  - value: EFFECTIVE
    label: 已生效
    source: code_enum
  - value: REJECTED
    label: 已拒绝
    source: code_enum
transitions:
  - from: INEFFECTIVE
    event: 接受加入集团
    to: EFFECTIVE
    evidence: "code_path:CustGroupRelApplication.java:1389"
  - from: INEFFECTIVE
    event: 拒绝加入集团
    to: REJECTED
    evidence: "code_path:CustGroupLicenseApplication.java:157"
```
