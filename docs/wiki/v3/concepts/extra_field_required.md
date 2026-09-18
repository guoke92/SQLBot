---
type: concept
title: 补充字段是否必填
page_key: extra_field_required
belong: concepts
domain: cust
status: draft
aliases: [补充字段, 银行分行名称必填, 补充字段企业角色维度]
maps_to: tenant_setting_config.bank_branch_property_requried
field_targets: [tenant_setting_config.bank_branch_property_requried, tenant_setting_config.finance_org_type_property_requried,
  tenant_setting_config.bank_branch_property_requried_config_cust_role, tenant_setting_config.finance_org_type_property_requried_config_cust_role]
sources: ['code_path:CustCompanyIfoEnchanceService.java:1672', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [finance_org_type_term, bank_branch_name]
adjudication: boundary
---

# 补充字段是否必填

document_claim:补充字段.md#13 / 补充字段企业角色维度.md#11：租户配置决定建档补充字段是否必填，并可按企业角色收窄。
现网必填列 *property_requried，角色列 *property_requried_config_cust_role。角色为空则视为不强制。不是企业上的取值列。

## 页面链接

- [[tables/tenant_setting_config]]
- [[dicts/tenant_setting_config__bank_branch_property_requried]]
- [[dicts/tenant_setting_config__finance_org_type_property_requried]]
- [[concepts/bank_branch_name]]
- [[concepts/finance_org_type_term]]
