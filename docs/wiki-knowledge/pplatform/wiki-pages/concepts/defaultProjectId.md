---
type: concept
title: "defaultProjectId"
page_key: defaultProjectId
belong: concepts
domain: "租户配置与运营邮件"
status: published
aliases: ["默认项目ID", "default_project_id"]
oid: 1

sources: ["semantic_analysis", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "tenant_setting_config.default_project_id"
field_targets: ["tenant_setting_config.default_project_id", "tenant_project.id"]
adjudication: boundary
also_confused_with: ["tenant_project.id"]
scope:
  databases: [lowcode_pplatform]
---

业务定位：默认项目 ID，是租户配置中的外键值，指向 tenant_project.id。

## 需求背景
无特定需求声明。

## 版本演进
- 暂无。

相关页面：[[tenant_setting_config]] [[tenant_project]] [[Excel导入默认项目ID合法校验]]