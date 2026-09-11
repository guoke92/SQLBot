---
type: concept
title: 端口
page_key: concept.port
domain: 客户角色与端口
status: draft
aliases:
  - 产品端口
  - 企业角色端口
oid: 1
scope:
  databases:
    - db_dist
sources:
  - db_dist: platform_product_cust_role
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
maps_to: platform_product_cust_role 记录，即 product_code + company_type_code 组合（如 AMS+SUPPLIER、DRAFT+CORE）
also_confused_with:
  - cust_role_info.role_type
  - platform_product_cust_role.company_type_code
adjudication: boundary
boundary: 『端口』是产品配置维度（某产品下允许某企业角色接入），落在 platform_product_cust_role；cust_role_info.role_type 是某具体企业在租户下已获得的角色，二者是模板定义与实例授权的关系。
field_targets:
  - platform_product_cust_role.company_type_code
  - platform_product_cust_role.product_code
contract_version: "0.1"
---

# 端口

「端口」（又称产品端口、企业角色端口）是业务口语，其落点是 [[tables/platform_product_cust_role]] 的一行记录，键为 product_code + company_type_code 组合，例如 AMS+SUPPLIER、DRAFT+CORE。它的语义是**某产品下允许某类企业角色接入**，因此天然是菜单/资源权限的配置粒度——[[calibers/effective-product-port]] 用它来枚举可配端口，[[rules/menu-port-config]] 以它为维度维护菜单配置。

## 需求背景

需求与界面语言统一使用「端口」一词描述产品下的角色配置项；该词在数据模型中没有独立表，需要折算为产品编码与企业角色编码的组合。使用文档时，凡见「端口」应理解为配置维度而非某企业的实际角色。

## 版本演进

- 「端口」一词逐渐从界面文案沉淀为配置模型口径：配置对象由菜单树转向 product_code + company_type_code 组合，保存方式为覆盖式重建。

## 关联

- [[tables/platform_product_cust_role]]
- [[concepts/company-role]]
- [[calibers/effective-product-port]]
- [[rules/menu-port-config]]