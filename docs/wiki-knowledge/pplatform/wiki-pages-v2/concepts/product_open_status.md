---
type: concept
title: 开通状态（产品开通）
page_key: concepts/product_open_status
domain: 租户产品
status: draft
aliases: [开通状态, open_status, 产品开通状态]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
  - db:cust_interworking_product
  - code:ProductOpenStatusEnum
  - code:CustProductActiveConstant
maps_to:
  - tenant_product.open_status
  - cust_interworking_product.open_status
field_targets:
  - table: tenant_product
    field: open_status
    values: ["N", "P", "Y"]
    process: processes/tenant_product_open_status
  - table: cust_interworking_product
    field: open_status
    values: [OPENED, OPENING]
    process: processes/interworking_product_open_status
adjudication: >
  「开通状态」指该租户/客户是否已经获得某产品能力，是推进态（含中间态），
  与「启用标记 enable」不同：enable 是配置是否生效的开关（见 calibers/product_enable_flag），
  也不等同于「项目是否生效」（见 calibers/project_effective）。
  同名字段在不同表使用不同字面量体系：租户产品用 N/P/Y，客户互通产品用 OPENED/OPENING，
  不可跨表直接比较。
also_confused_with:
  - calibers/product_enable_flag
  - calibers/project_effective
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

「开通状态」是本主题最容易被串用的术语：它在产品侧（[[tables/tenant_product]]）、客户侧（[[tables/cust_interworking_product]]）各自有同名列，但取值体系不同。业务上它回答「能不能用」，而不是「配置是否打开」。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该术语桥用于避免把开通状态与启用标记、项目生效混为一谈，具体口径见 [[calibers/product_enable_flag]]。

## 版本演进
- 租户产品侧代码枚举 ProductOpenStatusEnum 仅覆盖 Y/P，DB 另有 N；客户互通产品侧 DB 值 OPENED 与代码常量 CustProductActiveConstant.OPENED 的对应关系未被枚举基线覆盖。
- 两个产品线的字面量体系未统一，是历史演进遗留。

本页按 concept 约定不设锚点块，字段目标见 frontmatter。

相关：[[tenant_product]]
