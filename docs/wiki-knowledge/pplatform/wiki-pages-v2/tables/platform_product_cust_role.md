---
type: table
title: platform_product_cust_role（产品企业角色/端口表）
page_key: table.platform_product_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - 产品端口表
  - 产品企业角色配置表
  - platform_product_cust_role
oid: 1
scope:
  databases:
    - db_dist
sources:
  - db_dist: platform_product_cust_role
  - code_path:LocalTypeMenuService.java#listTenantProductMenuConfig
  - code_path:LocalTypeRoleController.java#listResourceAuthByProductCode
  - reqdoc:cust-role-port
contract_version: "0.1"
---

# platform_product_cust_role（产品企业角色/端口表）

> (document_claim，未证实)：本文档对产品编码的枚举描述与代码/DB 实测不一致，详见「版本演进」，相关内容不得用作口径。

platform_product_cust_role 是**产品维度的角色模板表**：一行代表「某平台产品（product_code）允许某类企业角色（company_type_code）接入」，业务口语称这一行为一个**端口**（见 [[concepts/port]]）。它是菜单/资源权限配置的维度来源——listTenantProductMenuConfig 正是按 product_code 取出该产品下全部端口，再逐端口配置可见菜单与按钮资源（见 [[rules/menu-port-config]]）。

与 [[tables/cust_role_info]] 的区别：本表是**产品配置模板**（允许谁接入），cust_role_info 是**租户内实例授权**（这家企业实际是什么角色）。

## 需求背景

需求文档用 companyType / productCode 两个维度描述端口配置。companyType 侧已由代码与 DB 证实；productCode 侧文档枚举未获证实（见下）。菜单资源列表还存在按 code 过滤的内置行为（见 [[rules/menu-resource-code-filter]]）。

## 版本演进

- (document_claim，未证实)：文档声称 productCode 典型值为 SCF / AMS / RVSFACTOR。DB 实测 platform_product_cust_role.product_code 为 ACCOUNT_PRODUCT/AMS/BEECREDIT/CROSSBORDER/DEALER/DRAFT/DRAFTQA/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER，未见 SCF；RVSFACTOR 实际以 RVSFACTOR_PC 出现。产品编码应以代码 ProductCodeEnum 与 DB 实测为准。
- 启用标志 enable 的引入使端口支持「下线但保留配置」，取有效端口时必须带 enable='Y'（见 [[calibers/effective-product-port]]）。



```ground:field
fields:
  - name: company_type_code
    meaning: |
      平台产品下的企业角色编码，业务上也称『端口』；作为菜单/资源权限配置的维度。
    evidence: db_dist
  - name: company_type_name
    meaning: |
      企业角色中文名（供应商/核心企业/金融机构/平台运营方/集团企业/项目公司等）。
    evidence: db_dist
  - name: product_code
    meaning: |
      所属平台产品编码（ACCOUNT_PRODUCT/AMS/DRAFT/ORDER/CROSSBORDER/STORAGE/VOUCHER/ACFLOW/RVSFACTOR_PC 等）。
    evidence: db_dist
  - name: name
    meaning: |
      产品名称（产融平台/国内信用证/应收易融/融易单等），用于展示。
    evidence: db_dist
  - name: enable
    meaning: |
      启用标志 Y/N，配置菜单端口时用于过滤有效端口。
    evidence: db_dist
```

## 关联

- [[concepts/port]]
- [[concepts/company-role]]
- [[tables/cust_role_info]]
- [[calibers/effective-product-port]]
- [[rules/menu-port-config]]
- [[rules/menu-resource-code-filter]]