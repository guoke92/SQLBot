---
type: concept
title: 品牌
page_key: brand
belong: concepts
domain: AMS联系人第三方对接
status: published
aliases: [租户, bizLabel]
oid: 1
sources:
  - code
contract_version: "0.1"
maps_to: "TenantSettingConfigDO.bandName"
field_targets: ["TenantSettingConfigDO.bandName"]
adjudication: boundary
also_confused_with: [项目]
boundary: "品牌对应租户设置中的bandName字段，用于第三方标识"
scope:
  databases: [lowcode_pplatform]
---

品牌是租户设置的标识，对应 TenantSettingConfigDO.bandName 字段，用于第三方系统标识。在 AMS 联系人第三方对接中，品牌可作为新增联系人并发锁 key 的组成部分。

## 需求背景
新增企业联系人并发锁 key 为 PPB:ADDENTERPRISECONTACT:{companyName}-{bizLabel}，bizLabel 即品牌标识。

## 版本演进
初始版本基于语义桥提取，明确品牌与项目的边界。

[[TenantSettingConfigDO]] [[enterprise_contact_concurrency_lock]]