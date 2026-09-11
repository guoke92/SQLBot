---
type: concept
title: 运营对接人与组别（op_contact）
page_key: concepts/op_contact
domain: 租户项目
status: draft
aliases: [运营对接人, op_contact_a, op_contact_b, op_contact_a_group, 风控对接人, 查验对接人]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
maps_to:
  - tenant_project.op_contact_a
  - tenant_project.op_contact_b
  - tenant_project.op_contact_a_group
  - tenant_project.risk_control_contact_a
  - tenant_project.risk_control_contact_b
  - tenant_project.verification_contact
field_targets:
  - table: tenant_project
    field: op_contact_a
    note: 运营对接人A；导入导出时按运营人员姓名/ID 转换
  - table: tenant_project
    field: op_contact_b
    note: 运营对接人B；数据库以 JSON 数组字符串存储，DTO 转为 List<String>
  - table: tenant_project
    field: op_contact_a_group
    note: 运营组别；导入时按运营对接人A的组别刷新
adjudication: >
  「对接人」是一组按角色区分的字段（运营 A/B、查验、风控 A/B），
  它们共用一个转换规则：导入导出时按运营人员姓名/ID 互转（见 rules/import_length_limits 之外的导入校验）。
  其中 B 类字段（op_contact_b、risk_control_contact_b）是复数语义，库中以 JSON 数组字符串存储；
  A 类字段是单值。组别 op_contact_a_group 只跟随 A 刷新。
also_confused_with:
  - concepts/project_tag
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

本术语桥把「对接人」这一族字段归并为一个概念：它们共享姓名/ID 转换与人员存在性校验，区别只在角色与是否支持多人。库中既存姓名也存 ID 的转换逻辑，要求读取时先明确当前存的是哪一侧。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该概念支撑项目导入导出与运营归属维护，见 [[tables/tenant_project]]。

## 版本演进
- B 类字段以 JSON 数组字符串入库、DTO 转 List<String>，是「单值 → 多值」扩展后留下的表达方式。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

相关：[[tenant_project]]
