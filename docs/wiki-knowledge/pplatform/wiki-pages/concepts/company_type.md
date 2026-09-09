---
type: concept
title: 企业角色
page_key: company_type
belong: concepts
domain: CA证书收费与订单
status: published
aliases: ["companyType"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_company.source_company_type / ca_fee_order.company_type"
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

“企业角色”描述企业在业务中的角色类型，如 SUPPLIER/CORE/PROJECT_COMPANY。它出现在企业台账的来源角色和订单中的企业角色上。

## 需求背景

不同企业角色可能影响收费策略、订单类型或项目配置，需要在企业维度和订单维度保持一致引用。

## 版本演进

v0.1 草稿：作为术语桥接建立，后续可补充角色枚举的权威来源与业务含义。

相关：[[ca_fee_company]]、[[ca_fee_order]]