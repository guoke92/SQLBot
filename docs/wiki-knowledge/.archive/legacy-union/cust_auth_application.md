---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-product-activation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 企业产品开通授权（一企业一产品一行，open_status 状态机）。
page_key: cust_auth_application
domain: 客户与建档
aliases:
- cust_auth_application
anchors:
- cust_auth_application
---
# cust_auth_application

企业产品开通授权（一企业一产品一行，open_status 状态机）。

```ground:table
table: cust_auth_application
description: 企业产品开通授权（一企业一产品一行，open_status 状态机）。
inactive: false
fields:
- name: open_status
  dictionary: open-status
- name: open_time
- name: ref_cust_auth_application_tenant_product
- name: ref_cust_company_info
```

```ground:relation
type: SHARED_KEY
left: cust_auth_application.ref_cust_company_info
right: cust_account_info.ref_cust_company_info
cardinality: many_to_many
status: proposed
evidence: code_path:ev-epa-open-activated
```
