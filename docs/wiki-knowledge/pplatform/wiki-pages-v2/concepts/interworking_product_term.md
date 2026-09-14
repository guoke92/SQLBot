---
type: concept
title: 互通产品
page_key: interworking_product_term
domain: 互通产品
status: draft
aliases: [互联互通产品, 互通产品线]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_interworking_product
  - db:cust_interworking_product
  - code:PlatformProductTypeEnum
maps_to: tenant_interworking_product.*
field_targets: [tenant_interworking_product.open_status, cust_interworking_product.open_status]
adjudication: boundary
boundary: 互通产品分租户侧 tenant_interworking_product 与客户侧 cust_interworking_product，两端状态常量不同；与租户通用产品 tenant_product 通过产品查询扩展点 scenario=INTERWORKING/GENERAL 区分。
also_confused_with: [tenant_product]
contract_version: "0.1"
belong: concepts
---

"互通产品"是与租户通用产品并列的产品线，租户侧落 [[tenant_interworking_product]]（状态见 [[tenant_interworking_product_opened]]），客户侧落 [[cust_interworking_product]]（状态见 [[cust_interworking_product_opened]]）。产品类型侧由 [[PlatformProductTypeEnum]] 的 INTERWORKING 标记。

## 需求背景
语义分析未附带需求文档锚点；该术语桥用于防止把互通产品误当作 [[tenant_product_term]] 处理。

## 版本演进
语义分析未记录该术语的版本演进。

---REVIEW: concept | 互通产品---
语义分析中 term_bridges 的"互通产品"条目被截断（原文止于 aliases 片段），本页 aliases/boundary 依据"租户产品"条目的 also_confused_with 与 adjudication 反向归纳，需以完整条目校正。
---END REVIEW---