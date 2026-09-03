---
type: concept
title: "dbTenantCode"
page_key: "dbTenantCode"
domain: "租户配置与运营邮件"
status: published
aliases: ["db_tenant_code", "数据租户标识", "数据库租户编码"]
oid: 1

sources: ["semantic_analysis", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "tenant_setting_config.db_tenant_code"
field_targets: ["tenant_setting_config.db_tenant_code"]
adjudication: boundary
also_confused_with: ["app_tenant_code（逻辑租户标识）"]
scope:
  databases: [lowcode_pplatform]
---

业务定位：数据租户标识，是数据隔离主键；与逻辑租户标识 app_tenant_code 区分。

## 需求背景
无特定需求声明。

## 版本演进
- 暂无。

相关页面：[[tenant_setting_config]] [[自营租户（LLS租户）]]