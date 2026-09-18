---
type: concept
title: 自主认证
page_key: self_auth
belong: concepts
domain: cust
status: draft
aliases: [接口建档, 接口认证, 注册认证]
maps_to: cust_company_info__identify_style.SELF
field_targets: [cust_company_info__identify_style.SELF, cust_company_info.identify_style]
sources: ['code_path:IdentifyTypeConstant.java:24', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [invite_customer_entry, change_identify_style]
adjudication: boundary
---

# 自主认证

IdentifyTypeConstant 注释：SELF=自主认证。需求「接口建档」「接口认证」口语也落这一码，没有单独的接口认证枚举。
document_claim:接口建档.md#15。不要和 INVITE 客户录入混。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__identify_style]]
- [[concepts/change_identify_style]]
- [[concepts/invite_customer_entry]]
