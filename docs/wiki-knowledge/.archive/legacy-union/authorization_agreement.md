---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 平台授权确认书（一行=企业×管理员×产品×角色；全局共享豁免租户行过滤）。
page_key: authorization_agreement
domain: CA认证与服务费
aliases:
- authorization_agreement
anchors:
- authorization_agreement
---
# authorization_agreement

平台授权确认书（一行=企业×管理员×产品×角色；全局共享豁免租户行过滤）。

```ground:table
table: authorization_agreement
description: 平台授权确认书（一行=企业×管理员×产品×角色；全局共享豁免租户行过滤）。
inactive: false
fields:
- name: act_procinst_id
- name: authed_status
  dictionary: authed-status
- name: cust_id
- name: cust_manager_id
- name: platform_product_code
```
