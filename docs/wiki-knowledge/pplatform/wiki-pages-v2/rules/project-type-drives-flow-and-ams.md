---
type: rule
title: 上线审批项目类型决定流程与 AMS 推送
page_key: project-type-drives-flow-and-ams
domain: 微企链立项与项目审批
status: draft
aliases:
  - STANDARD/REGULAR 决定 flow_code
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
belong: rules
---

上线审批表的 `project_type` 有两个受其影响的后果：一是决定 `wf_procdef_key`（走哪套工作流定义），二是决定是否推送 AMS。因此它不是纯展示字段，改值会直接改变流程走向与外部系统联动。

该列与立项申请表的同名列语义不同，见 [[concepts/project-type-domain-split]]；字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 上线审批项目类型决定流程与 AMS 推送
subject: tenant_project_approval.project_type
evidence: code
source_meaning: 上线审批项目类型：STANDARD(标准项目)/REGULAR(常规项目)，决定 flow_code 与是否推送 AMS
```