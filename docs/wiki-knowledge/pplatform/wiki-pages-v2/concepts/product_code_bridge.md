---
type: concept
title: 产品/项目编码术语桥（product_code / platform_product_code / product_id / project_id）
page_key: concept.product_code_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - product_code
  - platform_product_code
  - product_id
  - project_id
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[platform_product.product_code / name]
  - semantic:field_semantics[tenant_product.platform_product_code / db_tenant_code]
  - semantic:field_semantics[tenant_project.tenant_id / platform_product_code / product_id / name]
  - semantic:field_semantics[cust_project_rel.project_id / product_id]
contract_version: "0.1"
maps_to:
  - term: product_code
    target: platform_product.product_code
    evidence: code
  - term: platform_product_code
    target: platform_product.product_code
    evidence: code
  - term: product_id
    target: tenant_project.product_id
    evidence: code
  - term: project_id
    target: tenant_project.project_id
    evidence: code
field_targets:
  - platform_product.product_code
  - tenant_product.platform_product_code
  - tenant_project.platform_product_code
  - tenant_project.product_id
  - cust_project_rel.project_id
  - cust_project_rel.product_id
  - cust_project_rel.ref_cust_project_rel_platform_product
also_confused_with:
  - tenant_project.name
---

产品编码（字典表 [[tables/platform_product]].product_code）在租户产品、租户项目、企业项目关联三处分别以 platform_product_code、ref_cust_project_rel_platform_product 等形式出现；项目与产品 id 在关系表中以字符串存储。

## 需求背景

编码与 id 并存：product_code 是业务编码，product_id / project_id 是实体 id，列表展示需要的产品名称来自平台产品表，三者不可互替。

## 版本演进

v0：首次成页。