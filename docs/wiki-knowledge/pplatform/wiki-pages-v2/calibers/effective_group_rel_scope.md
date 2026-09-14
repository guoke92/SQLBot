---
type: caliber
title: 集团关系生效范围
page_key: effective_group_rel_scope
domain: cust_org_permission
status: draft
aliases: [集团关系生效范围, EFFECTIVE 过滤, 生效集团口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
belong: calibers
---

本口径限定集团树只展示已生效关系：[[cust_group_rel]].status='EFFECTIVE'。状态流转见 [[cust_group_rel_status]]，根节点识别另见 [[root_group_rel_scope]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 集团关系生效范围
predicate: "cust_group_rel.status = 'EFFECTIVE'"
scope: listSubCust 子公司平铺结果过滤
evidence: code_path:CustGroupRelApplication.java:listSubCust
```