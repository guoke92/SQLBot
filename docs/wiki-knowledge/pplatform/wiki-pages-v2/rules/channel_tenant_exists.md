---
type: rule
title: 渠道所属租户存在校验
page_key: channel_tenant_exists
domain: 准入接入
status: draft
aliases: [租户校验, 渠道所属租户不存在]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
belong: rules
---

渠道命中后，系统取其 `cust_access_secret.db_tenant_code`（见口径 [[calibers/channel_lookup]]），再去 `tenant_setting_config` 中查找对应租户配置：记录必须存在且 `enable = 'Y'`，否则抛出“渠道所属租户不存在”。

该规则确保租户配置完整，是 [[rules/channel_exists_and_enabled]] 之后的第二道闸门。注意它校验的是租户配置表的 `enable`，与接入密钥表的 `enable` 是两张表上的同名同义字段，判定时不可混用。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValue`；涉及的 `tenant_setting_config` 表字段级语义见页末 REVIEW 提示。

```ground:rule
name: 渠道所属租户存在校验
content: 根据渠道获取db_tenant_code后，查询TenantSettingConfig，必须存在且enable='Y'，否则抛出'渠道所属租户不存在'
impact: 确保租户配置完整
field_targets:
  - cust_access_secret.db_tenant_code
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.enable
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```