---
type: concept
title: "生效"
page_key: effective
belong: concepts
domain: "tenant-project"
status: published
aliases: ["已生效", "EFFECTIVE", "ACTIVE"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
maps_to: "tenant_project.project_status = 'EFFECTIVE'"
field_targets: ["tenant_project.project_status"]
adjudication: "synonym"
also_confused_with: ["INVLIAD", "INACTIVE"]
scope:
  databases: [lowcode_pplatform]
---

“生效”指租户项目状态为 EFFECTIVE，是项目生命周期中的有效状态。代码使用 ProjectStatusEnum.EFFECTIVE，需求文档中的 ACTIVE 仅为业务表述，不作为落库值。

## 需求背景
术语桥接识别出“生效”与 ACTIVE 的混用风险，需要统一映射到代码枚举 EFFECTIVE。

## 版本演进
v0.1 版本完成术语桥接，后续需确认需求文档中 ACTIVE 的使用范围。

相关：[[tenant_project]] [[tenant_project_lifecycle]] [[invalid]]