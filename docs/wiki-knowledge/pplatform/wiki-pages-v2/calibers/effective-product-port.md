---
type: caliber
title: 有效产品端口口径
page_key: caliber.effective-product-port
domain: 客户角色与端口
status: draft
aliases:
  - 有效端口口径
  - enable=Y 端口
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
  - db_dist: platform_product_cust_role.enable
contract_version: "0.1"
---

# 有效产品端口口径

配置菜单权限时，可取端口集合限定为 platform_product_cust_role 中 enable='Y' 的记录。listTenantProductMenuConfig 按 product_code 取该产品全部端口（企业角色）用于菜单配置，停用端口不进入配置面。

该口径决定了「某产品下能看到哪些端口 tab」，与 [[calibers/effective-company-role]] 属于不同表、不同层级：前者是产品配置维度（模板），后者是租户授权维度（实例）。

## 需求背景

需求文档要求菜单按产品与端口维护可配置项；实现侧以 enable='Y' 过滤有效端口，停用端口不展示也不可配。

## 版本演进

- 端口 enable 标志使产品可下线部分端口而保留历史菜单配置；配置保存为覆盖式重建（见 [[rules/menu-port-config]]）。

```ground:caliber
name: 有效产品端口口径
predicate: platform_product_cust_role.enable = 'Y'
scope: LocalTypeMenuService#listTenantProductMenuConfig 按 product_code 取该产品全部端口（企业角色）用于菜单配置
evidence: code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
```

## 关联

- [[tables/platform_product_cust_role]]
- [[concepts/port]]
- [[rules/menu-port-config]]