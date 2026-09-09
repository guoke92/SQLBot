---
type: rule
title: "已生效的成员单位关系不能重复接受/拒绝"
page_key: effective-relation-no-repeat
belong: rules
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_group_rel.status]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

该规则确保已生效的成员单位关系不可再执行接受或拒绝操作，避免状态混乱。

## 需求背景

- 当 `cust_group_rel.status = 'EFFECTIVE'` 时，拒绝或接受协议操作会抛出异常。

## 版本演进

- 暂无变更。

```ground:rule
name: 已生效的成员单位关系不能重复接受/拒绝
content: 当 cust_group_rel.status = 'EFFECTIVE' 时，拒绝签署协议或接受协议操作会抛出异常
impact: 确保已生效关系不可再操作
field_targets:
  - cust_group_rel.status
evidence: code_path:CustGroupLicenseApplication.checkCustGroup
```

相关：[[cust_group_rel]] [[effective-group-member-relation]] [[group-member-relation-status]]