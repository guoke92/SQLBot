---
type: concept
title: 简易认证
page_key: simple_auth
belong: concepts
domain: cust
status: draft
aliases: [简易建档]
maps_to: cust_company_info__identify_style.SIMPLE
field_targets: [cust_company_info__identify_style.SIMPLE, cust_company_info.identify_style]
sources: ['document_claim:产品需求规格说明书_产融平台V1.0.0.md#1036', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [invite_platform_entry, change_identify_style]
adjudication: boundary
---

# 简易认证

简易认证是 identify_style=SIMPLE。提交后状态走 AWAIT_CUST_CONFIRM → BUILD_SUCCESS，不走邀请审批中的 CUST_BUILDING。
document_claim:简易认证流程.md#13 描述人脸后还可开通 CA；现网以 CustCompanyCaPolicy 为准，见 simple_auth_ca_history。
「变更认证方式」是改 identify_style 列，不是新建一条简易认证企业。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__identify_style]]
- [[concepts/change_identify_style]]
- [[concepts/invite_platform_entry]]
