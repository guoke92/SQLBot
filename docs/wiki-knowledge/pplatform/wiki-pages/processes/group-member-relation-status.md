---
type: process
title: "集团成员单位关系状态"
page_key: group-member-relation-status
belong: processes
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

集团成员单位关系状态机描述 `cust_group_rel.status` 从初始未生效到接受/拒绝，以及通过再次发送通知回退为未生效的生命周期。状态包括未生效（INEFFECTIVE）、已生效（EFFECTIVE）、已拒绝（REJECTED）。

## 需求背景

- 关系初始为未生效，接受后变为已生效，拒绝后变为已拒绝。
- 已生效或已拒绝状态在发送通知后可回归未生效。

## 版本演进

- 暂无变更。

```ground:state_machine
name: 集团成员单位关系状态
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
    event: accept
    to: EFFECTIVE
    evidence: code_path:CustGroupLicenseApplication.accept
  - from: INEFFECTIVE
    event: reject
    to: REJECTED
    evidence: code_path:CustGroupLicenseApplication.reject
  - from: INEFFECTIVE
    event: effectGroupRel
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.effectGroupRel
  - from: REJECTED
    event: sendCustGroupRelNotice
    to: INEFFECTIVE
    evidence: code_path:CustGroupLicenseApplication.sendCustGroupRelNotice
  - from: EFFECTIVE
    event: sendCustGroupRelNotice
    to: INEFFECTIVE
    evidence: code_path:CustGroupLicenseApplication.sendCustGroupRelNotice
```

相关：[[cust_group_rel]] [[effective-group-member-relation]] [[ineffective-group-member-relation]] [[rejected-group-member-relation]]