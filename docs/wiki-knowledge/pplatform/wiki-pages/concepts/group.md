---
type: concept
title: "集团"
page_key: group
belong: concepts
domain: 集团与关联关系
status: published
aliases: ["集团公司", "根节点", "root company"]
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
maps_to: "cust_group_rel 中 root_flag='Y' 的记录，对应 CustCompanyTypeEnum.CORPORATION_COMPANY"
field_targets: []
adjudication: boundary
also_confused_with: ["核心企业"]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

“集团”是集团与关联关系中的顶级组织节点，对应集团关系树的根。集团由 `cust_group_rel` 中 `root_flag='Y'` 的记录标识，通常企业角色为 `CORPORATION_COMPANY`。

## 需求背景

- 集团是组织关系树的根，成员单位挂载其下。
- 与“核心企业”不同：核心企业是一种企业角色，可能作为集团成员但不是根。

## 版本演进

- 暂无变更。

相关：[[member-unit]] [[group-root-node]] [[cust_group_rel]]