---
type: rule
title: "删除集团关系必须校验在途业务"
page_key: delete-relation-check-business
belong: rules
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_group_rel.cust_id, cust_group_rel.root_cust_id]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

删除集团关系前，必须校验是否存在在途业务和额度，防止删除有业务关联的集团关系。

## 需求背景

- 删除集团前调用 `checkGroupMemberDeleteService` 和额度校验，如有在途业务则抛出异常。

## 版本演进

- 暂无变更。

```ground:rule
name: 删除集团关系必须校验在途业务
content: 删除集团前调用 checkGroupMemberDeleteService 和额度校验，如有在途业务则抛出异常
impact: 防止删除有业务关联的集团关系
field_targets:
  - cust_group_rel.cust_id
  - cust_group_rel.root_cust_id
evidence: code_path:CustGroupRelApplication.removeRootGroup
```

相关：[[cust_group_rel]] [[group-root-node]]