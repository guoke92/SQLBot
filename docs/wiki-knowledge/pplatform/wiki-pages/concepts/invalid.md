---
type: concept
title: "失效"
page_key: "concept/invalid"
domain: "tenant-project"
status: published
aliases: ["已失效", "INVLIAD", "INVALID", "INACTIVE"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
maps_to: "tenant_project.project_status = 'INVLIAD'"
field_targets: ["tenant_project.project_status"]
adjudication: "synonym"
also_confused_with: ["INVALID"]
scope:
  databases: [lowcode_pplatform]
---

“失效”指租户项目状态为 INVLIAD，是项目生命周期中的失效状态。INVLIAD 是代码枚举中的拼写错误，DB/代码均使用该值，不应改写为 INVALID。

## 需求背景
术语桥接识别出“失效”与 INVALID/INACTIVE 的混用风险，需要明确落库值。

## 版本演进
v0.1 版本完成术语桥接，后续需确认需求文档中 INACTIVE 的使用范围。

相关：[[tenant_project]] [[tenant_project_lifecycle]] [[tenant-effective-condition-check]]