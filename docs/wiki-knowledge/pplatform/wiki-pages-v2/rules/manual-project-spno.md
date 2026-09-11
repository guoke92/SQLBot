---
type: rule
title: 模拟立项编号规则
page_key: rule.manual-project-spno
domain: 项目报表/统计/上报
status: draft
aliases:
  - MN 编号规则
  - generateManualSpNo
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
---

# 模拟立项编号规则

模拟立项的 spNo 由后端按固定表达式生成，形如 MN-yyyyMMdd-XXXX，并强制 data_source = MANUAL；入参若已以 MN 开头则直接视为模拟立项编号。

## 需求背景

模拟立项用于演示与联调（见 [[processes/project-data-source]]），必须以编号前缀与真实立项区分，列表与导出按 spNo 前缀 MN 识别。编号表达式 `MN-%T{yyyyMMdd}#S4#` 中的 S4 表示四位顺序号，保证同日多单不重号。字段定义见 [[tables/wechat_project_approval_apply]]，落库路径受编辑白名单与历史保护约束（见 [[rules/edit-whitelist-and-field-history]]）。

## 版本演进

开发用导入（isManualSpNo）与手工新增共用同一前缀判定，说明模拟立项能力已从单条手工新增扩展为可批量注入；data_source 的写入被规则强制，不依赖调用方传值。

```ground:rule
name: "模拟立项编号规则"
content: "spNo 由后端生成，编号表达式 MN-%T{yyyyMMdd}#S4#（MN-yyyyMMdd-XXXX）；入参若已以 MN 开头则视为模拟立项编号；data_source 强制 MANUAL；列表与导出按 spNo 前缀 MN 识别。"
impact: "模拟立项手工新增与开发用导入"
field_targets:
  - "wechat_project_approval_apply.sp_no"
  - "wechat_project_approval_apply.data_source"
evidence: "code_path:ProjectStatisticsApplication.java:generateManualSpNo + ProjectStatisticsDevImportApplication.java:isManualSpNo"
```