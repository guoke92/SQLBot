---
type: rule
title: 已离职运营人员提示
page_key: departed_contact_tip
domain: 项目报表/统计/上报
status: draft
aliases:
  - 已离职运营人员提示
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportController.generateTextForProjectReport
contract_version: "0.1"
belong: rules
---

对 top_flag=1 的项目/企业，系统检查其对接人是否已离职（operation_user.deleted='Y' 且 enable='Y'）；命中时生成提示文本并写入记录（项目台账写 [[tables/tenant_project|tenant_project]].text，企业侧写 wec_project_operation_rel.text）。该提示在列表与详情两处都可读到。

## 需求背景

需求文档未单列此规则；规则内容来自 ProjectReportController 的文本生成方法。

## 版本演进

v0 契约首版。影响面：项目台账列表/详情。提示文本是派生结果，每次读取前刷新；operation_user 表本身不在本主题契约范围内，仅作为判定输入被引用。字段目标：tenant_project.text、wec_project_operation_rel.text。

```ground:rule
name: 已离职运营人员提示
content: top_flag=1的项目/企业，若对接人已离职（operation_user.deleted='Y'且enable='Y'），生成提示文本并更新到text字段
impact: 项目台账列表/详情
field_targets:
  - tenant_project.text
  - wec_project_operation_rel.text
evidence: code_path:ProjectReportController.generateTextForProjectReport
```