---
type: process
title: 联系人账号状态机
page_key: person_status_flow
domain: 经办人/联系人/管理员管理
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
  - cust_person_info.status
---

作用于联系人 `status`（[[activate_status]]）。替换管理员时旧管理员冻结、新行 EFFECT。

```ground:process
name: 联系人账号状态机
field: cust_person_info.status
states:
  - value: ADD
    label: 未激活
    source: code_enum
  - value: EFFECT
    label: 已激活
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
transitions:
  - from: ADD
    event: 激活联系人
    to: EFFECT
    evidence: "code_path:CustPersonApplication.java:852"
  - from: EFFECT
    event: 冻结联系人
    to: FREEZE
    evidence: "code_path:CustPersonApplication.java:841"
```
