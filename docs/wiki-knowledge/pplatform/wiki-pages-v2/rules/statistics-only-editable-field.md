---
type: rule
title: 统计页唯一可编辑列
page_key: statistics-only-editable-field
domain: 微企链立项与项目审批
status: draft
aliases:
  - EDITABLE_FIELDS
  - custom_field_statistics_one
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
belong: rules
---

项目统计页面上只有一列是可编辑的：`custom_field_statistics_one`（自定义字段一(统计用)）。其余列一律只读展示，包括与它名字相近的 `custom_field_one`——后者是企微导入路径维护的字段，不是统计页字段。

这种「同名兄弟字段分属不同写入路径」的设计是本表最容易误改的地方，字段对照见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 统计页唯一可编辑列
subject: wechat_project_approval_apply.custom_field_statistics_one
evidence: code
source_meaning: 自定义字段一(统计用)；统计页唯一可编辑列（EDITABLE_FIELDS）
```