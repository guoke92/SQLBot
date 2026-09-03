---
type: concept
title: "项目码"
page_key: "concept/project_code"
domain: "tenant-project"
status: published
aliases: ["渠道码", "channelCode"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
maps_to: "tenant_project.channel_code"
field_targets: ["tenant_project.channel_code"]
adjudication: "boundary"
also_confused_with: ["project_code"]
scope:
  databases: [lowcode_pplatform]
---

“项目码”指渠道码，存储在 tenant_project.channel_code，唯一且默认值为 QD#S6#。与另一编码字段 project_code 不同。

## 需求背景
术语桥接识别项目码与 project_code 的边界，避免混淆。

## 版本演进
v0.1 版本完成边界判定，后续需确认 project_code 的业务含义。

相关：[[tenant_project]] [[cust_project_code_record]]