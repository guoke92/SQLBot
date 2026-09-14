---
type: concept
title: 项目标签（project_tag）
page_key: project_tag
domain: 租户项目
status: draft
aliases: [项目标签, project_tag, 生产项目/测试项目/暂停项目]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
maps_to:
  - tenant_project.project_tag
field_targets:
  - table: tenant_project
    field: project_tag
    note: 中文可选生产项目、测试项目、暂停项目，入库转枚举值
adjudication: >
  项目标签是「项目性质」的分类标记（生产项目/测试项目/暂停项目），
  与 enable（是否逻辑删除，见 calibers/project_effective）、is_prd（是否生产数据，导入导出时 Y/N 转「是/否」）
  三者含义不同：is_prd 描述数据属性，project_tag 描述项目用途，enable 描述记录是否有效。
also_confused_with:
  - calibers/project_effective
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
---

项目标签在导入侧以中文录入，落库时转成枚举值，导出侧再还原为可读文案。它解决的是「这个项目是生产、测试还是暂停」的分类问题，而 [[tables/tenant_project]] 的 is_prd 只回答数据是否来自生产。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。

## 版本演进
- 中文与枚举的双向转换说明该字段经历过「自由文本 → 受控枚举」的演进。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

相关：[[tenant_project]]
