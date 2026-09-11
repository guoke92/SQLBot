---
type: concept
title: 企业类型
page_key: company_type
domain: 企业建档与认证
status: draft
aliases:
  - 企业角色
  - 客户角色
  - cust_company_type
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_company_type
contract_version: "0.1"
maps_to: cust_company_info.cust_company_type
adjudication: synonym
also_confused_with: []
boundary: 企业类型、企业角色、客户角色均指同一概念，存储为JSON数组字符串。
sources: ["enrich:wiki-admin"]
---

“企业类型”“企业角色”“客户角色”是同一概念的不同叫法，对应字段 `cust_company_info.cust_company_type`。该字段以 **JSON 数组字符串**存储，例如 `["SUPPLIER"]`、`["CORE"]`，说明一个企业可同时承担多个角色。

该概念在语义分析中未发现与其他术语的混淆项（`adjudication: synonym`），是一组纯同义词归一；读取时需按 JSON 数组解析，不能按单值枚举直接比较。

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据语义分析建立 concept 页，归一企业类型 / 企业角色 / 客户角色三个同义叫法。

相关：[[cust_company_info]]
