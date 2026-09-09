---
type: concept
title: "运营对接人B"
page_key: op_contact_b
belong: concepts
domain: "tenant-project"
status: published
aliases: ["opContactB"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
maps_to: "tenant_project.op_contact_b / cust_project_rel.op_contact_b"
field_targets: ["tenant_project.op_contact_b", "cust_project_rel.op_contact_b"]
adjudication: "boundary"
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

“运营对接人B”字段在数据库存储为 JSON 数组字符串（运营人员 ID），代码层在 List<String> 与 JSON 之间转换，涉及 tenant_project 与 cust_project_rel 两表。

## 需求背景
术语桥接确认该字段跨表存在，且存储格式为 JSON 数组字符串，需在数据契约中明确。

## 版本演进
v0.1 版本完成字段边界描述，后续需确认转换逻辑细节。

相关：[[tenant_project]] [[cust_project_rel]]