---
type: concept
title: project_type 同名异域
page_key: concept/project-type-domain-split
domain: 微企链立项与项目审批
status: draft
aliases:
  - 项目类型歧义
  - project_type 同名不同域
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.project_type
  - tenant_project_approval.project_type
field_targets:
  - table: wechat_project_approval_apply
    field: project_type
  - table: tenant_project_approval
    field: project_type
adjudication: 两表的 project_type 列名相同但取值域完全不同：立项申请表中是主项目(MAIN)/子项目(SUB)，上线审批表中是标准项目(STANDARD)/常规项目(REGULAR)。跨表引用 project_type 时必须显式带上表名。
also_confused_with:
  - tenant_project_approval.project_type 决定 flow_code 与 AMS 推送，立项表的 project_type 不承担该职责
sources: ["enrich:wiki-admin"]
---

这是本主题里最容易写错的同名列：两个核心表都叫 `project_type`，但一个描述项目结构层级（主/子），另一个描述上线审批的流程类型（标准/常规），并且后者还承担了决定工作流定义与是否推送 AMS 的职责（见 [[rules/project-type-drives-flow-and-ams]]）。

在 SQL、接口参数、前端字典任意一层省略表名限定都可能造成误用；本概念仅做歧义标注，不改变任何一列的取值域。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[tables/tenant_project_approval]]。

相关：[[wechat_project_approval_apply]]
