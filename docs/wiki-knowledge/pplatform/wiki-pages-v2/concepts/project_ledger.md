---
type: concept
title: 项目台账
page_key: project_ledger
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目台账
  - 项目运营配置
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportController.generateTextForProjectReport
  - code_path:ProjectReportApplication.exportProjectReport
contract_version: "0.1"
maps_to: tenant_project
field_targets: []
adjudication: synonym
also_confused_with: []
belong: concepts
---

「项目台账」是业务口头的模块名，其物理承载是 [[tables/tenant_project|tenant_project]]。台账视角关注的是项目的运营配置与责任人健康度：项目状态是否生效、是否生产数据、对接人是否离职（写入 text 提示文本），以及导出时企业行的来源归属。

## 需求背景

需求文档与导出功能对该模块使用两个名字：「项目台账」与「项目运营配置」——导出文件名使用「项目运营配置」。本页判定二者为同义（adjudication=synonym），不做语义切分。

## 版本演进

v0 契约首版。相关规则与口径：[[rules/departed_contact_tip|已离职运营人员提示]]、[[calibers/project_ledger_export_source|项目台账导出企业source判定]]、[[calibers/project_ledger_company_query|产融项目台账企业查询口径]]。