---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: CA 服务费企业缴费台账（按统一社会信用代码一行，全局共享：不参与租户行级过滤， tenant_id 仅溯源）。跨租户读需 db_tenant_code=all。
page_key: ca_fee_company
domain: CA认证与服务费
aliases:
- ca_fee_company
anchors:
- ca_fee_company
---
# ca_fee_company

CA 服务费企业缴费台账（按统一社会信用代码一行，全局共享：不参与租户行级过滤， tenant_id 仅溯源）。跨租户读需 db_tenant_code=all。

```ground:table
table: ca_fee_company
description: CA 服务费企业缴费台账（按统一社会信用代码一行，全局共享：不参与租户行级过滤， tenant_id 仅溯源）。跨租户读需 db_tenant_code=all。
inactive: false
fields:
- name: certification_no
- name: fee_locked
- name: locked_annual_fee
- name: pay_status
  dictionary: company-pay-status
- name: renew_remind_sent
- name: service_end
- name: service_start
- name: special_annual_fee
- name: special_config_flag
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_order.certification_no
right: ca_fee_company.certification_no
cardinality: many_to_one
status: proposed
evidence: code_path:ev-cfc-order-paid
```
