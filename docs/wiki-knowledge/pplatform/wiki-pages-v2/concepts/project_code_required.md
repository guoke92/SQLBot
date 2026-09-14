---
type: concept
title: 项目码是否必填
page_key: project_code_required
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [projectCodeRequired, project_code_required, 项目码必填]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.checkBeforeSave"
contract_version: "0.1"
maps_to: tenant_setting_config.project_code_required
field_targets:
  - tenant_setting_config.project_code_required
  - tenant_setting_config.default_project_id
adjudication: boundary
also_confused_with:
  - tenant_setting_config.default_project_id
belong: concepts
field_targets: [tenant_setting_config.project_code_required]
---

「项目码是否必填」指 [[tenant_setting_config]].project_code_required（Y/N）。它是触发条件，被约束对象是 `default_project_id`：前者为 Y 时后者必填。二者是一组条件与结果，不能互换理解，联动规则见 [[rule_project_code_default_project]]。

## 需求背景
部分租户要求项目维度的成本/归属管理，必须先指定默认关联项目，否则后续单据无法定位项目。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。