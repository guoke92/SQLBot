---
type: concept
title: 企业角色
page_key: enterprise_role
domain: 客户角色与端口
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
field_targets:
  - cust_company_info.cust_company_type
  - cust_role_info.role_type
maps_to: cust_company_info.cust_company_type
adjudication: synonym
also_confused_with: [cust_person_info.user_type]
---

供应商/核心企业/金融机构落 [[company_type]]。企业主档是企业当前角色；`cust_role_info` 是按角色切片的激活行；联系人 `company_type` 表示人绑在哪一切片。
