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
title: 企业信息变更记录（在途判定 + 审核状态机；变更拒绝安全更新的 EXISTS 锚点表）。
page_key: cust_change_record
domain: 客户与建档
aliases:
- cust_change_record
anchors:
- cust_change_record
---
# cust_change_record

企业信息变更记录（在途判定 + 审核状态机；变更拒绝安全更新的 EXISTS 锚点表）。

```ground:table
table: cust_change_record
description: 企业信息变更记录（在途判定 + 审核状态机；变更拒绝安全更新的 EXISTS 锚点表）。
inactive: false
fields:
- name: alter_mode
- name: alter_type
- name: cust_id
- name: msg_send
- name: oper_cust_id
- name: status
  dictionary: change-status
```
