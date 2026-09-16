---
type: process
title: 企业角色激活状态机
page_key: role_status_flow
domain: 客户角色与端口
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
  - cust_role_info.status
---

作用于 [[cust_role_info]].status。与联系人共用激活字典，列不同。

```ground:process
name: 企业角色激活状态机
field: cust_role_info.status
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
    event: 激活角色
    to: EFFECT
    evidence: "code_path:CustSyncEventProcessor.java:2118"
  - from: EFFECT
    event: 冻结角色
    to: FREEZE
    evidence: "code_path:CustRoleApplication.java:74"
  - from: EFFECT
    event: 注销角色
    to: WRITEOFF
    evidence: "code_path:CustRoleApplication.java:84"
```
