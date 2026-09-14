---
type: caliber
title: 已生效集团关系
page_key: effective_group_rel
domain: 集团关系
status: draft
aliases:
  - status=EFFECTIVE
  - 生效成员单位口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: calibers
---

# 已生效集团关系

口径判断：`cust_group_rel.status = 'EFFECTIVE'`，即签署完成、关系已生效的集团成员单位关系。

## 需求背景

集团成员查询 `listSubCust` 仅返回该状态节点，未生效/已拒绝关系不进入成员视图，状态来源见 [[cust_group_rel_status]]、术语见 [[member_unit]]。

## 版本演进

- 生效可由 `accept` 签署、根企业建档成功、`effectGroupRel` 外部回调三条路径达成，落地路径较多，排查成员缺失时需同时看签署与回调。

```ground:caliber
name: 已生效集团关系
predicate: cust_group_rel.status = 'EFFECTIVE'
scope: listSubCust 仅返回该状态节点
evidence: code_path:CustGroupRelApplication.java:listSubCust
```