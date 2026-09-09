---
type: rule
title: 租户保存前置校验
page_key: tenant-save-precheck
belong: rules
domain: tenant-config-operation-email
status: published
aliases: [租户保存前置校验, checkBeforeSave]
oid: 1
sources: [code, reqdoc]
contract_version: "0.1"
field_targets: [tenant_setting_config.code, tenant_setting_config.db_tenant_code, tenant_setting_config.default_project_id, tenant_setting_config.name, tenant_setting_config.project_code_required, tenant_setting_config.tenant_flg_en, tenant_setting_config.uni_social_credit_code]
scope:
  databases: [lowcode_pplatform]
---

该规则定义了租户保存前的前置校验逻辑，包括统一社会信用代码合法性、项目码必填约束、默认项目必填、唯一性校验等。

## 需求背景

为保证租户配置数据的合法性与唯一性，保存前必须执行多项校验。若校验失败，抛出异常阻止保存。

## 版本演进

- 初版（v0.1）：基于 `TenantDomainService.checkBeforeSave` 实现。
- BR-001 差异：代码未校验 `dbTenantCode` 合法性，未校验默认项目 ID 属于该租户且生效，仅校验了默认项目非空。

```ground:rule
name: 租户保存前置校验
content: "校验统一社会信用代码合法性；项目码必填=Y时默认项目必填；唯一性校验（code、name、db_tenant_code、tenant_flg_en、域名等）"
impact: 校验失败抛出异常，阻止保存
field_targets:
  - tenant_setting_config.uni_social_credit_code
  - tenant_setting_config.project_code_required
  - tenant_setting_config.default_project_id
  - tenant_setting_config.code
  - tenant_setting_config.name
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.tenant_flg_en
evidence: "code_path:TenantDomainService.checkBeforeSave"
```

[[tenant_setting_config]] [[数据租户标识]] [[tenant_flg_en]]