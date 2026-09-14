---
type: rule
title: 菜单端口筛选规则
page_key: menu_port_filter
domain: 客户角色与端口
status: draft
aliases:
  - 端口菜单筛选
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:LocalTypeMenuService.java:listTenantProductMenuConfig
  - code_path:LocalTypeMenuService.java:listProductCustMenu
contract_version: "0.1"
belong: rules
---

该规则描述菜单配置页上“端口（企业角色）× 菜单”的筛选与选中逻辑，连接 [[platform_product_cust_role]] 与 tenant_product_menu。

## 需求背景

根据产品 code 查询 platform_product_cust_role 获取所有端口（企业角色），再按租户和产品查询已配置菜单，标记选中状态。端口取值来源口径见 [[valid_product_cust_role]]，术语见 [[port]]。

## 版本演进

- v0（draft）：依据 LocalTypeMenuService 两个方法成页；tenant_product_menu 表结构未在证据范围内。

```ground:rule
name: 菜单端口筛选规则
content: "根据产品 code 查询 platform_product_cust_role 获取所有端口（企业角色），再按租户和产品查询已配置菜单，标记选中状态。"
impact: 影响 tenant_product_menu 配置
field_targets:
  - platform_product_cust_role.company_type_code
  - tenant_product_menu.company_type
evidence: "code_path:LocalTypeMenuService.java:listTenantProductMenuConfig, listProductCustMenu"
```