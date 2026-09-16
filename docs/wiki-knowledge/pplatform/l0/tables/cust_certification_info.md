---
type: table
title: cust_certification_info
page_key: cust_certification_info
belong: tables
status: draft
aliases: []
anchors:
- cust_certification_info
sources:
- database_schema:lowcode_pplatform.cust_certification_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# cust_certification_info

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### certification

`name`, `remark`, `certification_type`, `face_business_no`, `verify_score`

### related_entity

`organization_id`, `ref_cust_company_info`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### auto_verify

`auto_verify_status`, `auto_verify_msg`, `auto_verify_time`, `auto_verify_count`, `auto_verify_data`

### manual_verify

`manual_verify_status`, `manual_verify_msg`, `manual_verify_time`, `manual_verify_count`

## 字段

```ground:table
table: cust_certification_info
database: lowcode_pplatform
description: cust_certification_info
inactive: false
primary_key: []
grain: 一行一记录（?）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: tenant
  title: 租户
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: certification
  title: 认证信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: related_entity
  title: 关联主体
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: workflow
  title: 流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: auto_verify
  title: 自动核验
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: manual_verify
  title: 人工核验
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
fields:
- name: id
  data_type: number
  description: ''
  nullable: true
  cluster: common
- name: code
  data_type: string
  description: ''
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: ''
  nullable: true
  cluster: certification
- name: enable
  data_type: string
  description: ''
  nullable: true
  cluster: common
  dictionary: cust_certification_info_enable
- name: remark
  data_type: string
  description: ''
  nullable: true
  cluster: certification
- name: create_by
  data_type: string
  description: ''
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: ''
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: ''
  nullable: true
  cluster: common
- name: update_by
  data_type: string
  description: ''
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: ''
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: ''
  nullable: true
  cluster: common
- name: act_procinst_id
  data_type: string
  description: ''
  nullable: true
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: ''
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: ''
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: ''
  nullable: true
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: ''
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: ''
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: ''
  nullable: true
  cluster: related_entity
- name: ref_cust_company_info
  data_type: string
  description: ''
  nullable: true
  cluster: related_entity
- name: certification_type
  data_type: string
  description: ''
  nullable: true
  cluster: certification
  dictionary: cust_certification_info_certification_type
- name: auto_verify_status
  data_type: string
  description: ''
  nullable: true
  cluster: auto_verify
  dictionary: cust_certification_info_auto_verify_status
- name: auto_verify_msg
  data_type: string
  description: ''
  nullable: true
  cluster: auto_verify
- name: auto_verify_time
  data_type: temporal
  description: ''
  nullable: true
  cluster: auto_verify
- name: auto_verify_count
  data_type: number
  description: ''
  nullable: true
  cluster: auto_verify
- name: auto_verify_data
  data_type: string
  description: ''
  nullable: true
  cluster: auto_verify
- name: manual_verify_status
  data_type: string
  description: ''
  nullable: true
  cluster: manual_verify
  dictionary: cust_certification_info_manual_verify_status
- name: manual_verify_msg
  data_type: string
  description: ''
  nullable: true
  cluster: manual_verify
- name: manual_verify_time
  data_type: temporal
  description: ''
  nullable: true
  cluster: manual_verify
- name: manual_verify_count
  data_type: number
  description: ''
  nullable: true
  cluster: manual_verify
- name: face_business_no
  data_type: string
  description: ''
  nullable: true
  cluster: certification
- name: verify_score
  data_type: number
  description: ''
  nullable: true
  cluster: certification
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_certification_info.ref_cust_company_info
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_certification_info.ref_cust_company_info
```
