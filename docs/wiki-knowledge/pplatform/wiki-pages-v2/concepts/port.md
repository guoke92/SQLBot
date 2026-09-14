---
type: concept
title: 端口
page_key: port
domain: 客户角色与端口
status: draft
aliases:
  - 产品端口
  - 企业角色端口
oid: 1
scope:
  databases:
    - db
sources:
  - db_dist:platform_product_cust_role
  - code_path:LocalTypeMenuService.java
contract_version: "0.1"
maps_to:
  - platform_product_cust_role.company_type_code
also_confused_with:
  - 菜单端口
  - 系统接入端口
adjudication: synonym
boundary: "在客户角色与菜单配置语境中，'端口'指 platform_product_cust_role 表中定义的产品下可支持的企业角色（company_type_code），每个端口对应一个企业角色。"
belong: concepts
---

“端口”在客户角色与菜单配置语境下是“平台产品支持的企业角色”的口语表述，落点见 [[platform_product_cust_role]].company_type_code，与 [[company_role]] 属于同义表述的不同视角：企业角色强调客户侧身份，端口强调产品侧可选项。

## 需求背景

菜单配置以端口为最小勾选单位：先取产品下的有效端口（口径见 [[valid_product_cust_role]]），再匹配租户已配置菜单，形成 tenant_product_menu 记录，规则见 [[menu_port_filter]]。因此“端口”易与菜单端口、系统接入端口混淆，需按表定锚。

## 版本演进

- v0（draft）：依据 term_bridges 与菜单配置代码路径首次成页。