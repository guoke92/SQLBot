---
type: concept
title: "tenant_flg_en"
page_key: "tenant_flg_en"
domain: "租户配置与运营邮件"
status: published
aliases: ["项目标识（产融）", "projectMark", "租户英文标识"]
oid: 1

sources: ["semantic_analysis", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "tenant_setting_config.tenant_flg_en 或 tenant_project.tenant_flg_en（需根据上下文区分）"
field_targets: ["tenant_setting_config.tenant_flg_en", "tenant_project.tenant_flg_en"]
adjudication: boundary
also_confused_with: ["tenant_project.tenant_flg_en（项目级标识）"]
scope:
  databases: [lowcode_pplatform]
---

业务定位：本概念标识租户配置或项目中的英文标识，具体映射需根据上下文区分，Excel 导入中的“项目标识(产融 tenant_flg_en)”对应租户配置表字段。

## 需求背景
无特定需求声明。

## 版本演进
- 暂无。

相关页面：[[tenant_setting_config]] [[tenant_project]] [[自营租户（LLS租户）]]