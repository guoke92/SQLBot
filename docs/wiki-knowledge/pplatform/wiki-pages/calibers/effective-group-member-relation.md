---
type: caliber
title: "生效集团成员单位关系"
page_key: effective-group-member-relation
belong: calibers
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

生效集团成员单位关系口径用于定义状态为 `EFFECTIVE` 的关系，适用于集团树查询和列表过滤。

## 需求背景

- 仅 `status = 'EFFECTIVE'` 的关系才视为已生效的集团成员单位关系。

## 版本演进

- 暂无变更。

```ground:caliber
name: 生效集团成员单位关系
predicate: cust_group_rel.status = 'EFFECTIVE'
scope: 集团树查询、列表过滤（如listSubCust）
evidence: code
```

相关：[[cust_group_rel]] [[group-member-relation-status]]