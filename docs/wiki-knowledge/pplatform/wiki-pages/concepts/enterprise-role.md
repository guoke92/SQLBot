---
type: concept
title: 企业角色
page_key: enterprise-role
domain: 企业建档与准入
status: published
aliases: [客户角色, 公司类型]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: cust_company_info.cust_company_type 或 cust_role_info.role_type
also_confused_with: ["用户类型", "人员类型"]
adjudication: synonym
boundary: cust_company_type 存储企业角色数组，cust_role_info 按角色和应用拆分
field_targets: []
scope:
  databases: [lowcode_pplatform]
---

# 企业角色

企业角色描述企业或客户在业务中的身份，如供应商、核心企业、资金方等。数据侧可能同时存在于 `cust_company_info.cust_company_type`（JSON 数组）和 `cust_role_info.role_type`（按角色和应用拆分），二者语义同义但存储粒度不同。

## 需求背景

需求文档中“企业类型必选：核心企业、供应商、经销商、资金方等”，代码映射中发现 `SPY->SUPPLIER`、`CE->CORE`、`CPT->FINANCE`、`OPE->PLATFORM_OPERATOR`，未发现经销商映射。该差异为散文性记录。

## 版本演进

本概念由术语桥提炼，`adjudication` 为 `synonym`，两个字段表达同一概念的不同粒度。

相关概念：[[admin]]、[[enterprise-customer]]；相关口径：[[supplier-company]]

相关：[[cust_company_info]] [[cust_role_info]]
