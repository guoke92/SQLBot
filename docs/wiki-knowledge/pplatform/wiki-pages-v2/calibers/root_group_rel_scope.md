---
type: caliber
title: 根集团关系范围
page_key: root_group_rel_scope
domain: cust_org_permission
status: draft
aliases: [根集团关系, level=1, 根节点口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
belong: calibers
---

本口径以 [[cust_group_rel]].level=1 识别根节点，与 root_flag（根标识写死 "Y"）互为印证。注意此处用的是集团关系记录自身，而非企业主键，见 [[group_id]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 根集团关系范围
predicate: "cust_group_rel.level = 1"
scope: 根节点识别
evidence: code_path:CustGroupRelApplication.java:processGroupByParent
```