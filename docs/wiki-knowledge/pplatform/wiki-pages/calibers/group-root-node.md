---
type: caliber
title: "集团根节点"
page_key: group-root-node
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_group_rel.cust_id, cust_group_rel.root_cust_id, cust_group_rel.root_flag]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

集团根节点口径用于在构建集团树时识别根节点，以根标识和根企业 ID 组合判断。

## 需求背景

- 根节点必须同时满足 `root_flag = 'Y'` 且 `root_cust_id = cust_id`。

## 版本演进

- 暂无变更。

```ground:caliber
name: 集团根节点
predicate: cust_group_rel.root_flag = 'Y' AND cust_group_rel.root_cust_id = cust_group_rel.cust_id
scope: 构建集团树时识别根节点
evidence: code
```

相关：[[cust_group_rel]] [[group]] [[member-unit]]