---
type: concept
title: 跨租户强制补签授权书
page_key: cross_tenant_resign
belong: concepts
domain: tenant
status: draft
aliases: [跨租户补签授权书, 强制重签授权书]
maps_to: tenant_setting_config.sign_flag
field_targets: [tenant_setting_config.sign_flag]
sources: ['code_path:CustCompanyInfoApplication.java:6259', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [authorization_book, electronic_auth_flag, auth_supplement_flag,
  auth_channel_flag]
adjudication: boundary
---

# 跨租户强制补签授权书

document_claim:跨租户补签授权书.md#18。catalog 注释「接收跨贴牌数据是否强制重签授权书」。
现网 Y 则跨租户同步要补签。不是 generate_electronic_auth_flag，也不是企业上的补签开关。Y/N 不编字典页。

## 页面链接

- [[tables/tenant_setting_config]]
- [[dicts/tenant_setting_config__sign_flag]]
- [[concepts/auth_channel_flag]]
- [[concepts/auth_supplement_flag]]
- [[concepts/authorization_book]]
- [[concepts/electronic_auth_flag]]
