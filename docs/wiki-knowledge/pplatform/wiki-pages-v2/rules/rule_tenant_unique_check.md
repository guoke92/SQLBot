---
type: rule
title: 租户唯一性校验
page_key: rule_tenant_unique_check
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [checkUnique, 租户唯一校验, 已存在，请确认!]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code_path:TenantDomainService.java:checkUnique"
contract_version: "0.1"
belong: rules
---

保存与迁移前对多列逐个做唯一性校验，任一命中即拒绝并提示『已存在，请确认!』。参与校验的列包括 uniSocialCreditCode、code、name、dbTenantCode、tenantFlgEn、devDomain、sitDomain、uatDomain、prdDomain；当 needHfive='Y' 时追加四个 H5 域名的唯一校验。

注意：bandName 的唯一校验已被注释禁用——它虽在代码中出现，但当前不产生拦截，引用时不要把它当作生效规则。

涉及字段：[[tenant_setting_config]] 的 code、db_tenant_code、tenant_flg_en、uni_social_credit_code；标识语义见 [[db_tenant_code]]、[[tenant_flg_en]]。

## 需求背景
租户标识、编码、名称与各环境域名一旦重复会导致路由与数据归属错乱，因此在写入前统一做去重校验，把冲突拦截在保存阶段。

## 版本演进
v0.1（本页）：首版契约，锚点证据来自语义分析；bandName 校验已禁用，如需恢复须复核。

```ground:rule
name: 租户唯一性校验
content: "对 uniSocialCreditCode / code / name / dbTenantCode / tenantFlgEn / devDomain / sitDomain / uatDomain / prdDomain 逐个做 count==0 校验；needHfive='Y' 时追加四个 H5 域名唯一；bandName 的唯一校验已被注释禁用"
impact: "保存/迁移去重；命中唯一约束给出『已存在，请确认!』"
field_targets:
  - tenant_setting_config.code
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.tenant_flg_en
  - tenant_setting_config.uni_social_credit_code
evidence: "code_path:TenantDomainService.java:checkUnique"
```