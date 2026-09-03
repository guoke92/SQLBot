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
title: 供应商邀请记录（progress 派生自企业 cust_build_status，按企业名+租户匹配写入）。
page_key: cust_invite_info
domain: 客户与建档
aliases:
- cust_invite_info
anchors:
- cust_invite_info
---
# cust_invite_info

供应商邀请记录（progress 派生自企业 cust_build_status，按企业名+租户匹配写入）。

```ground:table
table: cust_invite_info
description: 供应商邀请记录（progress 派生自企业 cust_build_status，按企业名+租户匹配写入）。
inactive: false
fields:
- name: invite_cust_id
- name: invite_from
- name: invite_time
- name: progress
  dictionary: invite-progress
```
