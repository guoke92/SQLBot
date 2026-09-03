---
type: caliber
title: "已拒绝集团成员单位关系"
page_key: rejected-group-member-relation
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

已拒绝集团成员单位关系口径定义拒绝协议后的状态。

## 需求背景

- 当关系被拒绝后，状态变为 `REJECTED`。

## 版本演进

- 暂无变更。

```ground:caliber
name: 已拒绝集团成员单位关系
predicate: cust_group_rel.status = 'REJECTED'
scope: 拒绝协议后的状态
evidence: code
```

相关：[[cust_group_rel]] [[group-member-relation-status]]