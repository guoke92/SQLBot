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
title: CA 服务费订单（全局共享不参与租户行过滤）。乐观锁 version；操作轨迹 operate_logs JSON 追加。
page_key: ca_fee_order
domain: CA认证与服务费
aliases:
- ca_fee_order
anchors:
- ca_fee_order
---
# ca_fee_order

CA 服务费订单（全局共享不参与租户行过滤）。乐观锁 version；操作轨迹 operate_logs JSON 追加。

```ground:table
table: ca_fee_order
description: CA 服务费订单（全局共享不参与租户行过滤）。乐观锁 version；操作轨迹 operate_logs JSON 追加。
inactive: false
fields:
- name: agreement_signed
- name: annual_fee
- name: certification_no
- name: close_reason
- name: company_id
- name: invoice_status
- name: order_no
- name: order_status
  dictionary: order-status
- name: order_type
  dictionary: order-type
- name: pay_amount
- name: pay_method
- name: pay_time
- name: project_id
- name: service_end
- name: service_start
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_order.certification_no
right: ca_fee_company.certification_no
cardinality: many_to_one
status: proposed
evidence: code_path:ev-cfc-order-paid
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_order.project_id
right: ca_fee_project_config.project_id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-cfc-order-close
```
