---
type: concept
title: 租户产品
page_key: tenant_product_term
domain: 租户产品
status: draft
aliases: [tenant_product, 租户产品配置, 租户产品]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - db:tenant_interworking_product
  - db:cust_interworking_product
maps_to: tenant_product.*
field_targets: [tenant_product.code, tenant_product.open_status, tenant_product.enable, tenant_product.platform_product_code]
adjudication: boundary
boundary: tenant_product 是租户级通用产品开通表；tenant_interworking_product/cust_interworking_product 是互通产品线，产品查询扩展点 scenario=INTERWORKING/GENERAL 区分。
also_confused_with: [tenant_interworking_product, cust_interworking_product]
contract_version: "0.1"
belong: concepts
---

"租户产品"指租户开通了哪个平台产品的记录，落在 [[tenant_product]] 表；判定期（开通状态）见 [[tenant_product_open_status]]。该词容易与互通产品线混淆，判别边界见下方 frontmatter 的 boundary。注意：语义分析给出的 `maps_to` 为表级 `tenant_product`，本页按表级映射记作 `tenant_product.*`，具体字段见 `field_targets`。

## 需求背景
语义分析未附带需求文档锚点；术语桥的作用是让"租户产品/互通产品/客户互通产品"在口径与查询中不串用。

## 版本演进
语义分析未记录该术语的版本演进。