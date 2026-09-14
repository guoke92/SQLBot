---
type: concept
title: 产品开通状态
page_key: product_open_status
domain: 平台产品配置
status: draft
aliases: [openStatus, open_status, product_status, 开通状态]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustProductDomainService.java
  - code:TenantProductApplication.java
  - code:ProductStatusEnum.java
contract_version: "0.1"
maps_to: cust_auth_application.open_status
also_confused_with:
  - tenant_product.open_status
  - platform_product.product_status
adjudication: boundary
boundary: "三张表语义不同：platform_product.product_status 为产品定义层生效状态('0'/'1')；tenant_product.open_status 为租户上架状态(Y/P)；cust_auth_application.open_status 为企业级开通状态(OPENED/OPENING/NOT_OPENED)。需求文档称 PENDING/ACTIVE/CANCEL 与实现不符。"
belong: concepts
field_targets: [cust_auth_application.open_status]
---

「产品开通状态」是需求文档与接口层最易混淆的术语：同一句「产品是否开通」在三张表上对应三套取值域与三种业务含义。本概念页用于固定辨析边界，默认指企业级的 [[cust_auth_application]] `open_status`。

## 需求背景

- 定义层：[[platform_product]] 的 `product_status`（'0' 待生效 / '1' 已生效），见 [[platform_product_status]]。
- 上架层：[[tenant_product]] 的 `open_status`（Y 已上架 / P 处理中），见 [[tenant_product_open_status]]。
- 开通层：[[cust_auth_application]] 的 `open_status`（OPENED / OPENING / NOT_OPENED），见 [[cust_product_open_status]]。

需求文档把租户上架状态写作 PENDING / ACTIVE / CANCEL，实现为 P / Y，属文档与实现的命名漂移。

## 版本演进

- 三套语义在实现中长期并存，未做字段改名，仅通过本概念页的边界裁定区分。

关联：[[cust_auth_application]]、[[tenant_product]]、[[platform_product]]、[[cust_product_open_status]]、[[tenant_product_open_status]]、[[platform_product_status]]