---
type: concept
title: 租户编码术语桥（db_tenant_code / tenant_code / sysChannel）
page_key: concept.db_tenant_code_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - db_tenant_code
  - tenant_code
  - 租户编码
  - sysChannel
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.db_tenant_code]
  - semantic:field_semantics[cust_project_rel.tenant_code / db_tenant_code]
  - semantic:field_semantics[tenant_setting_config.db_tenant_code]
  - semantic:field_semantics[tenant_setting_config.sso_tenant_chanel]
contract_version: "0.1"
maps_to:
  - term: db_tenant_code
    target: tenant_setting_config.db_tenant_code
    evidence: code
  - term: tenant_code
    target: tenant_setting_config.db_tenant_code
    evidence: code
  - term: sysChannel
    target: tenant_setting_config.sso_tenant_chanel
    evidence: code
field_targets:
  - cust_company_info.db_tenant_code
  - cust_project_rel.tenant_code
  - cust_project_rel.db_tenant_code
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.sso_tenant_chanel
---

数据隔离键的统一术语：db_tenant_code 是全局隔离键，cust_project_rel 中 tenant_code 与 db_tenant_code 同值写入；对接运营中台时，sysChannel 取 tenant_setting_config.sso_tenant_chanel。

## 需求背景

Provider 层默认按当前租户隔离，跨租户查询需显式设置（见 [[rules/cross_tenant_query_all]]）。sysChannel 参与鉴权签名（见 [[rules/token_sign_md5]]），与 db_tenant_code 不是同一字段，但都源自租户配置（[[tables/tenant_setting_config]]）。

## 版本演进

v0：首次成页。