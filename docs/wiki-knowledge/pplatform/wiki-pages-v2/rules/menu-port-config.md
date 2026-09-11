---
type: rule
title: 菜单端口配置按企业角色维护
page_key: rule.menu-port-config
domain: 客户角色与端口
status: draft
aliases:
  - listTenantProductMenuConfig 端口配置
  - saveTenantProductMenuConfig
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
  - code_path:LocalTypeMenuService.java#saveTenantProductMenuConfig
contract_version: "0.1"
---

# 菜单端口配置按企业角色维护

listTenantProductMenuConfig 以 [[tables/platform_product_cust_role]] 的 company_type_code（即 [[concepts/port]]）为维度，为每个端口列出可配置菜单（listProductCustMenu）与按钮资源（listProductCustMenuResource）；保存时先删除该租户该产品下已配菜单与资源，再批量重建。配置是**覆盖式**的。

影响：端口是菜单权限配置的粒度——同产品不同端口可以有完全不同的菜单集；保存动作不是增量合并，部分保存会导致未提交的配置被删除。取端口集合时须遵守 [[calibers/effective-product-port]]。

## 需求背景

需求文档要求「按产品与端口为租户配置可见菜单与按钮资源」，本规则是该诉求的实现口径，并明确了配置粒度为 company_type_code。

## 版本演进

- 保存由增量维护改为先删后建，简化冲突处理，代价是必须整表单提交。
- 端口列表读取增加 enable 过滤，使停用端口不再进入可配面。

```ground:rule
name: 菜单端口配置按企业角色维护
content: listTenantProductMenuConfig 以 platform_product_cust_role 的 company_type_code 为维度，为每个端口列出可配置菜单(listProductCustMenu)与按钮资源(listProductCustMenuResource)，保存时先删除该租户该产品下已配菜单与资源再批量重建。
impact: 『端口』是菜单权限配置的粒度，配置为覆盖式
field_targets:
  - platform_product_cust_role.company_type_code
  - platform_product_cust_role.product_code
evidence: code_path:LocalTypeMenuService.java#listTenantProductMenuConfig/#saveTenantProductMenuConfig
```

## 关联

- [[concepts/port]]
- [[tables/platform_product_cust_role]]
- [[calibers/effective-product-port]]
- [[rules/menu-resource-code-filter]]