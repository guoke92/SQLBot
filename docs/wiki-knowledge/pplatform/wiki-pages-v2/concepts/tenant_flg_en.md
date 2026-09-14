---
type: concept
title: 项目标识（英文）
page_key: tenant_flg_en
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [tenantFlgEn, tenant_flg_en, projectMark, 租户英文标识, 项目标识(英文)]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.getFirstByTenantFlgEn / afterCreate 强制置为 db_tenant_code"
  - "code:TenantDomainService.existEarlyLLsTenant / doSaveTenantShare"
contract_version: "0.1"
maps_to: tenant_setting_config.tenant_flg_en
field_targets:
  - tenant_setting_config.tenant_flg_en
adjudication: boundary
also_confused_with:
  - tenant_setting_config.tenant_flag_zh
  - tenant_project.tenant_flg_en
  - cust_company_info.tenant_flg_en
belong: concepts
field_targets: [tenant_setting_config.tenant_flg_en]
---

「项目标识（英文）」是 XYC 体系下租户的唯一标识，落在 [[tenant_setting_config]].tenant_flg_en。`afterCreate` 初始化时会把它强制置为 db_tenant_code；同一 `db_tenant_code` 下可以存在多个不同 tenant_flg_en，这正是自营假租户共享落表的判定条件（见 [[rule_share_self_tenant]]）。

边界：Excel 导入的『项目标识(产融 tenant_flg_en)』实际定位的是 tenant_setting_config.tenant_flg_en（走 `getFirstByTenantFlgEn`），不是 tenant_project；`tenantFlagZh` 只是中文展示名。

## 需求背景
产融体系下同一个数据租户可承载多个项目标识，导入与查询都必须以 tenant_flg_en 作为定位键，避免误落到项目主数据表。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。