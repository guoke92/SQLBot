---
type: concept
title: 平台产品与租户产品
page_key: platform_product_vs_tenant_product
domain: 租户产品
status: draft
aliases: [平台产品, 租户产品, platform_product_code, 产品两层结构]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:tenant_project
  - db:tenant_product_menu
maps_to:
  - tenant_product.platform_product_id
  - tenant_product.platform_product_code
  - tenant_product.ref_tenant_product_project_code
  - tenant_project.ref_tenant_project_product_code
field_targets:
  - table: tenant_product
    field: platform_product_id
    note: 平台产品 id；与 tenant_id 组成唯一键
  - table: tenant_product
    field: ref_tenant_product_project_code
    note: 租户产品-平台产品关联编码
  - table: tenant_project
    field: ref_tenant_project_product_code
    note: 关联租户产品 code
adjudication: >
  平台产品是产品定义层（platform_product_id / platform_product_code），
  租户产品是定义在某租户上的实例（tenant_id + platform_product_id 唯一，见 rules/tenant_product_unique_key）。
  项目通过 ref_tenant_project_product_code 挂在租户产品下，而不是直接挂在平台产品下；
  因此在按产品统计时，应先落到租户产品再汇总，避免把平台产品 code 当作租户产品 code 使用。
also_confused_with:
  - concepts/product_open_status
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
---

「平台产品—租户产品—项目」是三级结构：平台产品给出产品编号（ACFLOW/BEECREDIT 等），租户产品给出该租户下的实例及其融资口径，项目是实例下的具体业务载体（[[tables/tenant_project]]）。菜单配置（[[tables/tenant_product_menu]]）按产品 code 维度下发，其取值与 platform_product_code 不完全是同一套值。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该术语桥用于避免在查询与统计中混用两级产品的 code。

## 版本演进
- 产品 code 存在多套值域：platform_product_code（含 DRAFT/DRAFTQA/STORAGE/VOUCHER）与 tenant_product_menu.product_code（含 ACCOUNT_PRODUCT）并不一致。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

相关：[[tenant_product]]
