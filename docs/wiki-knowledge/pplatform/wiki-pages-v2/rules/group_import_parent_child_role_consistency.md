---
type: rule
title: 集团成员导入父子角色一致性
page_key: group_import_parent_child_role_consistency
domain: cust_org_permission
status: draft
aliases: [父子角色一致, 集团导入角色校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
belong: rules
---

该规则阻断同链角色混挂的集团树，判定基于 [[cust_company_info]].cust_company_type（JSON 数组，多角色），语义见 [[company_type]]；关系落库见 [[cust_group_rel]]、[[cust_group_rel_status]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 集团成员导入父子角色一致性
content: 若父级企业已存在，其 cust_company_type 必须包含子级申报的企业角色；父级尚未存在时，同一父级下所有子级角色必须一致。
impact: 阻断同链角色混挂的集团树。
field_targets:
  - cust_company_info.cust_company_type
evidence: code_path:CustGroupRelApplication.java:checkRoleExcelData
```