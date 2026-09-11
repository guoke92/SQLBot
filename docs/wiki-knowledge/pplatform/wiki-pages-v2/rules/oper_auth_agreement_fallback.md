---
type: rule
title: 子账号授权书模板未配置时回落 Nacos 值
page_key: rule.oper_auth_agreement_fallback
domain: 平台内部服务对接
status: draft
aliases:
  - 授权书模板回落
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.oper_auth_agreement]
contract_version: "0.1"
---

租户未配置 oper_auth_agreement 时，使用 Nacos 中的 operAuthAgreement 值作为授权书模板 id。

## 需求背景

这是租户配置（[[tables/tenant_setting_config]]）与配置中心之间的兜底约定，属于内部服务对接中「配置缺失不应阻断流程」的处理方式。

## 版本演进

v0：首次成页。

```ground:rule
name: 子账号授权书模板未配置时回落 Nacos 值
field: tenant_setting_config.oper_auth_agreement
condition: "未配置时"
effect: "回落 Nacos 值 operAuthAgreement"
evidence: code
```