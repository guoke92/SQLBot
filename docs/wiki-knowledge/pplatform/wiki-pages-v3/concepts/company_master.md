---
type: concept
title: 企业主档身份
page_key: company_master
domain: 基线
status: draft
aliases: [企业, 客户]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:cust_company_info"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
maps_to: cust_company_info.code
field_targets:
  - cust_company_info.code
  - cust_company_info.certification_no
adjudication: boundary
boundary: 建档场景主档是 cust_company_info；收费场景主档是 ca_fee_company
also_confused_with: [ca_fee_company.certification_no]
---

「企业」在建档场景落 [[cust_company_info]]（业务编码 `code`，信用代码 `certification_no`）。收费场景的当前缴费结论落 [[ca_fee_company]]，两表用信用代码对齐，但**主档角色不同**：

- [[company_build]]：本表是主档
- [[ca_fee]]：本表只是身份源，不要展开建档状态机

企业主档名称列是 `name`（客户名称）。收费台账上的 `company_name` 是拷贝，不当 JOIN 键。
