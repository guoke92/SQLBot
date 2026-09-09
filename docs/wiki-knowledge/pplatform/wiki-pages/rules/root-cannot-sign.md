---
type: rule
title: "集团根节点不能执行签署协议操作"
page_key: root-cannot-sign
belong: rules
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_group_rel.root_flag]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

该规则防止集团根节点进行协议签署操作，确保根节点的组织地位不被协议流程改变。

## 需求背景

- 当 `cust_group_rel.root_flag = 'Y'` 时，不接受或拒绝协议操作。

## 版本演进

- 暂无变更。

```ground:rule
name: 集团根节点不能执行签署协议操作
content: 当 cust_group_rel.root_flag = 'Y' 时，不接受/拒绝协议操作
impact: 控制集团根节点不能进行协议签署
field_targets:
  - cust_group_rel.root_flag
evidence: code_path:CustGroupLicenseApplication.checkCustGroup
```

相关：[[cust_group_rel]] [[group-root-node]] [[group]]