---
type: concept
title: 逻辑租户标识与数据租户标识
page_key: logical_vs_db_tenant_code
domain: 互通产品
status: draft
aliases: [app_tenant_code, db_tenant_code, 逻辑租户, 数据租户]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_interworking_product
  - db:tenant_product_menu_res
maps_to:
  - tenant_interworking_product.app_tenant_code
  - tenant_interworking_product.db_tenant_code
  - tenant_product_menu_res.db_tenant_code
field_targets:
  - table: tenant_interworking_product
    field: app_tenant_code
    values: [GREENTOWNAT, JHYL, base, hylg]
  - table: tenant_interworking_product
    field: db_tenant_code
    values: ["ISOLATE_TAG_*", LN1, "beehive-scf.qhhrly.cn", mengniu, yunyingzhongtai]
  - table: tenant_product_menu_res
    field: db_tenant_code
    values: [LN1, "beehive-scf.qhhrly.cn", ning]
adjudication: >
  app_tenant_code 是逻辑租户标识（应用/业务视角的租户），db_tenant_code 是数据租户标识（数据隔离视角）。
  二者在 tenant_interworking_product 上成对出现，取值集合并不相同，不能互相替代；
  菜单资源表只带 db_tenant_code，说明菜单配置按数据隔离维度下发。
also_confused_with:
  - concepts/platform_product_vs_tenant_product
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
---

本术语桥用于区分「逻辑租户」与「数据租户」两个在库中形似而语义不同的列。前者对应业务上签约的主体，后者对应数据落库/隔离的归属；测试数据中的 ISOLATE_TAG_* 前缀进一步印证后者是隔离维度的技术标识。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该区分影响互通产品配置与菜单资源的下发范围，见 [[tables/tenant_interworking_product]]、[[tables/tenant_product_menu_res]]。

## 版本演进
- db_tenant_code 同时存在简码（LN1、ning）与域名（beehive-scf.qhhrly.cn）两种形态，命名规范未统一。
- 未提供版本记录；无 (document_claim，未证实) 主张。

本页按 concept 约定不设锚点块。

相关：[[tenant_interworking_product]]
