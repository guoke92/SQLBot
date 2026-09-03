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
title: 企业银行账户（含小额打款认证 auth_state 状态机 + 默认账户标记）。 全局共享不参与租户行过滤。
page_key: cust_account_info
domain: 客户与建档
aliases:
- cust_account_info
anchors:
- cust_account_info
---
# cust_account_info

企业银行账户（含小额打款认证 auth_state 状态机 + 默认账户标记）。 全局共享不参与租户行过滤。

```ground:table
table: cust_account_info
description: 企业银行账户（含小额打款认证 auth_state 状态机 + 默认账户标记）。 全局共享不参与租户行过滤。
inactive: false
fields:
- name: auth_state
  dictionary: auth-state
- name: default_account_flag
- name: error_try_count
- name: error_try_time
- name: payment_remaining_count
- name: trace_no
- name: trans_id
```

```ground:relation
type: SHARED_KEY
left: cust_auth_application.ref_cust_company_info
right: cust_account_info.ref_cust_company_info
cardinality: many_to_many
status: proposed
evidence: code_path:ev-epa-open-activated
```
