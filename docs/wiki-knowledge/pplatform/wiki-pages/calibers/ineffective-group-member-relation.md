---
type: caliber
title: "未生效集团成员单位关系"
page_key: ineffective-group-member-relation
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

未生效集团成员单位关系口径描述初始状态或待处理协议的关系。

## 需求背景

- 关系状态为 `INEFFECTIVE` 时，可执行接受或拒绝操作。

## 版本演进

- 暂无变更。

```ground:caliber
name: 未生效集团成员单位关系
predicate: cust_group_rel.status = 'INEFFECTIVE'
scope: 初始状态、待处理协议
evidence: code
```

相关：[[cust_group_rel]] [[group-member-relation-status]]