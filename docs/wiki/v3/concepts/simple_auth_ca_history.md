---
type: concept
title: 简易认证与电子签章
page_key: simple_auth_ca_history
belong: concepts
domain: cust
status: draft
aliases: [简易建档开通CA, 开通电子签章]
maps_to: cust_company_info.need_register_ca
field_targets: [cust_company_info.identify_style, cust_company_info.need_register_ca]
sources: ['code_path:CustCompanyCaPolicy.java:26', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [simple_auth]
adjudication: boundary
---

# 简易认证与电子签章

早期需求（简易认证流程、V1.7/V1.17 升级建档）允许简易认证开通 CA。
document_claim:简易认证流程.md#29 写「若简易建档开通了 CA，则人脸后还需同意 CFCA 协议」。
V1.26 变更时「开通电子签章」置灰。现网 CustCompanyCaPolicy 在 identify_style=SIMPLE 时强制四个签章字段为 N。
document_claim:供票产品开通校验规则.md#17：简易认证/未开通签章/非总公司不能开通供票。
问「简易认证是否开通签章」以现网代码为准：不开通。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__identify_style]]
- [[dicts/cust_company_info__need_register_ca]]
- [[concepts/simple_auth]]
