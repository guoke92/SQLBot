---
type: caliber
title: 集团根节点
page_key: group_root_node
domain: 集团关系
status: draft
aliases:
  - root_flag=Y
  - 根企业口径
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: calibers
---

# 集团根节点

口径判断：`cust_group_rel.root_flag = 'Y'`，即集团根企业所在的关系节点。

## 需求背景

根节点是集团树的树根，也是签署流程的边界：`checkCustGroup` 拒绝对根节点做签署/拒绝操作（[[root_group_no_operation]]）。术语辨析见 [[group_root]]。

## 版本演进

- DB `root_flag='Y'` 29 条与 `level=1` 的 29 条一致，当前两者可作为同一批节点的双重判据。

```ground:caliber
name: 集团根节点
predicate: cust_group_rel.root_flag = 'Y'
scope: checkCustGroup 拒绝对根节点做签署/拒绝操作
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```