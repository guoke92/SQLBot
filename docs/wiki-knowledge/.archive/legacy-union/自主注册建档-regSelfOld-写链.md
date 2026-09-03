---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-onboarding@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: process
title: 自主注册建档（regSelfOld 写链）
page_key: 自主注册建档-regSelfOld-写链
domain: 企业建档
aliases: []
---
# 自主注册建档（regSelfOld 写链）

完整读写流转：先读企业→按企业 code 读联系人→升级管理员→推送运营→回写状态与中台用户 id→落建档记录。

```ground:process
process: 自主注册建档（regSelfOld 写链）
stages:
- stage: 自主注册建档（regSelfOld 写链）
  trigger: 自助注册建档请求，带企业 id 与联系人 id
  effects:
  - op: read
    table: cust_company_info
    fields:
    - id
    - code
  - op: read
    table: cust_person_info
    fields:
    - id
    - ref_cust_company_info
  - op: update
    table: cust_person_info
    fields:
    - user_type
  - op: update
    table: cust_company_info
    fields:
    - check_status
  - op: update
    table: cust_person_info
    fields:
    - platform_user_id
  - op: insert
    table: cust_build_record
    fields:
    - cust_id
    - person_id
  transitions: []
```

## 关联
- [[cust_build_record]]
- [[cust_company_info]]
- [[cust_person_info]]
