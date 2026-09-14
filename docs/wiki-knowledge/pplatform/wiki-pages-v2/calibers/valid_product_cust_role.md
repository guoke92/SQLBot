---
type: caliber
title: 平台产品有效端口
page_key: valid_product_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - enable=Y 端口
  - 产品有效企业角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:LocalTypeMenuService.java:listTenantProductMenuConfig
  - db_dist:platform_product_cust_role
contract_version: "0.1"
belong: calibers
---

口径「平台产品有效端口」筛选 [[platform_product_cust_role]] 中 enable='Y' 的记录，得到某产品下当前生效的企业角色（端口）列表。

## 需求背景

菜单配置服务先按产品 code 取出有效端口，再按租户与产品查询已配置菜单并标记选中状态，见 [[menu_port_filter]]。术语“端口”的释义见 [[port]]。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认，当前库内 enable=Y 共 53 条。

```ground:caliber
name: 平台产品有效端口
predicate: "platform_product_cust_role.enable = 'Y'"
scope: 产品下支持的企业角色（端口）列表
evidence: "code_path:LocalTypeMenuService.java:listTenantProductMenuConfig；db_dist: enable Y 53"
```