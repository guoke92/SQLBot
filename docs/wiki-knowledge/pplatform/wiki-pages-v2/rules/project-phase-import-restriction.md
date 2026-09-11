---
type: rule
title: 立项阶段不落库且审批通过后不可导入
page_key: rule/project-phase-import-restriction
domain: 微企链立项与项目审批
status: draft
aliases:
  - 立项阶段导入校验
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

「立项阶段」不是库内状态，它只用于展示与导入校验，落库时会被忽略；并且当企微审批已通过后，导入不允许再写「立项阶段」。也就是说导入模板接受的取值范围与库内实际存储的项目阶段并不是同一个集合。

这一点直接决定了导入校验报错与库内取值对不上时应当以库内为准，见 [[processes/project-phase]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 立项阶段不落库且审批通过后不可导入
subject: wechat_project_approval_apply.project_phase
evidence: code
source_meaning: 项目阶段：IMPLEMENTATION(实施阶段)/持续运营/挂起；TERMINATION 为历史值读时归一为挂起；『立项阶段』仅用于展示与导入校验、不落库
```