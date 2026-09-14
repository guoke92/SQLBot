---
type: rule
title: 菜单资源列表自动过滤指定 code
page_key: menu-resource-code-filter
domain: 客户角色与端口
status: draft
aliases:
  - filterMenuByCode
  - 菜单 code 过滤
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:LocalTypeRoleController.java#listResourceAuthByProductCode
  - reqdoc:cust-role-port
contract_version: "0.1"
belong: rules
---

# 菜单资源列表自动过滤指定 code

配置端口菜单资源时，列表会对若干内置菜单 code 做自动剔除，使它们不出现在可配置列表中。文档只描述了其中一个 code，代码中实际剔除三个。

使用要点：这些 code 属**内置保留项**，不要试图通过菜单配置为其开权限，也不要期望在列表中看到它们；需求文档与实现存在数量差异，以代码为准。

## 需求背景

需求文档主张「菜单 code='0891344a3a4442179e98819cbe926ced' 的记录在列表中自动过滤」，该主张已由代码证实，但代码实际剔除三个 code（见锚点块），文档列举不全。

## 版本演进

- 过滤清单由 1 个扩展到 3 个 code，文档未同步更新，形成文档与实现的枚举落差。

```ground:rule
name: 菜单资源列表自动过滤指定 code
content: 菜单 code='0891344a3a4442179e98819cbe926ced' 的记录在列表中自动过滤
impact: 被过滤的内置菜单不进入可配置资源列表，不应为其配置端口权限
evidence: code_path:LocalTypeRoleController.java#listResourceAuthByProductCode（filterMenuByCode 实际剔除 3 个 code: 0891344a3a4442179e98819cbe926ced、81b9d705e8a14d6088bcf341884e70d8、16bcb2ed1daf4b739a5aad6e791aefa4，文档仅列出 1 个） + reqdoc:cust-role-port
```

## 关联

- [[rules/menu-port-config]]
- [[tables/platform_product_cust_role]]
- [[concepts/port]]