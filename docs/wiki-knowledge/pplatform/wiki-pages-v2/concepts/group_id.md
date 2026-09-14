---
type: concept
title: groupId
page_key: group_id
domain: cust_org_permission
status: draft
aliases: [rootGroupId, parentGroupId, id]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
maps_to: cust_group_rel.id
field_targets: [cust_group_rel.id, cust_group_rel.cust_id, cust_group_rel.root_cust_id]
adjudication: boundary
also_confused_with:
  - cust_group_rel.cust_id / root_cust_id
belong: concepts
---

rootGroupId/parentGroupId 指向 [[cust_group_rel]] 自身记录 id，rootCustId/parentCustId 指向 [[cust_company_info]].id。树构建一律用 group id，业务归属一律用 cust id；在集团查询与导入场景里混用会直接改变结果集。相关流程见 [[cust_group_rel_status]]，范围见 [[root_group_rel_scope]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。