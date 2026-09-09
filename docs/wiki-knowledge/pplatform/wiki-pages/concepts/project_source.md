---
type: concept
title: "项目来源/交易平台"
page_key: project_source
belong: concepts
domain: "tenant-project"
status: published
aliases: ["source", "项目来源"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
maps_to: "tenant_project.source"
field_targets: ["tenant_project.source"]
adjudication: "boundary"
also_confused_with: ["platform_product_code"]
scope:
  databases: [lowcode_pplatform]
---

“项目来源/交易平台”指 tenant_project.source 字段，代码会按 ProductCodeEnum 转中文名称显示，与平台产品编码 platform_product_code 不同。

## 需求背景
术语桥接识别项目来源与平台产品编码的边界，避免语义重叠。

## 版本演进
v0.1 版本完成边界判定，后续需确认 source 与 platform_product_code 的关联关系。

相关：[[tenant_project]]