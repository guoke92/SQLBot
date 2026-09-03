---
type: concept
title: bg_color（背景颜色）
page_key: concepts.bg_color
domain: tenant-config-operation-email
status: published
aliases: [背景颜色, 灰度颜色]
oid: 1
sources: [db, code_enum, term_bridge]
contract_version: "0.1"
maps_to: "tenant_setting_config.bg_color"
field_targets: ["tenant_setting_config.bg_color"]
adjudication: boundary
also_confused_with: []
boundary: "取值 L=彩色, G=灰色，null=未设置"
scope:
  databases: [lowcode_pplatform]
---

`bg_color` 表示租户背景颜色配置，取值范围为 L（彩色）、G（灰色）、null（未设置）。该字段受全局背景色开关联动影响，同时有缓存支持。

## 需求背景

租户界面需要支持灰度/彩色视觉状态，背景颜色字段需精确表达当前租户的颜色配置，并区分未设置状态。

## 版本演进

- 初版（v0.1）：术语桥判定为 boundary，明确取值边界。

[[tenant_setting_config]] [[tenant-bg-color]]