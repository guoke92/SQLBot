---
type: concept
title: 企业类型
page_key: concept_cust_type
domain: 企业变更与运营变更
status: published
aliases: ["客户类型", "cust_type"]
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_change_cfg.cust_type / cust_change_record.cust_type"
field_targets: ["cust_change_cfg.cust_type", "cust_change_record.cust_type"]
adjudication: "boundary"
also_confused_with: ["cust_company_info.cust_company_type"]
coverage_note: 术语边界
scope:
  databases: [lowcode_pplatform]
---

“企业类型”（或客户类型）用于区分企业/个人客户分类，出现在变更配置与变更记录中。它与具体的企业角色（如供应商、核心企业）不同，后者由 `cust_company_type` 描述。

## 需求背景

边界说明：`cust_type` 是企业/个人客户分类；`cust_company_type` 是具体企业角色。

## 版本演进

暂无。

相关：[[cust_change_cfg]] [[cust_change_record]]
