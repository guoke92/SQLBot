---
type: concept
title: 客户状态
page_key: concept_cust_status
domain: 企业变更与运营变更
status: published
aliases: ["custStatus"]
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_company_info.cust_status"
field_targets: ["cust_company_info.cust_status"]
adjudication: "boundary"
also_confused_with: ["cust_company_info.check_status", "cust_person_info.status"]
coverage_note: 术语边界
scope:
  databases: [lowcode_pplatform]
---

“客户状态”指企业业务状态，由 `cust_company_info.cust_status` 承载，如 EFFECT（正常）、FREEZE（冻结）、CHANGE（变更中）等。它不是审核状态，也不是联系人个人账号状态。

## 需求背景

边界说明：`cust_status` 表示企业业务状态；`check_status` 表示审核流程状态；`cust_person_info.status` 表示联系人账号状态。

## 版本演进

暂无。

相关：[[cust_company_info]]
