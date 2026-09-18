---
type: table
title: cust_certification_info
page_key: cust_certification_info
belong: tables
status: draft
anchors: [cust_certification_info]
sources: ['database_schema:lowcode_pplatform.cust_certification_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_certification_info__enable, cust_certification_info__certification_type,
  cust_certification_info__auto_verify_status, cust_certification_info__manual_verify_status]
---

# cust_certification_info

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### tenant

`app_tenant_code`, `db_tenant_code`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### reference

`organization_id`, `ref_cust_company_info`

### certification

`certification_type`, `face_business_no`, `verify_score`

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
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: act_procinst
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: reference
  title: 外部关联标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: certification
  title: 认证主体信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: auto_verify
  title: 自动核查
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
- key: manual_verify
  title: 人工核查
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_certification_info
fields:
- name: id
  data_type: number
  cluster: common
- name: code
  data_type: string
  cluster: common
- name: name
  data_type: string
  cluster: common
- name: enable
  data_type: string
  cluster: common
  dictionary: cust_certification_info__enable
- name: remark
  data_type: string
  cluster: common
- name: create_by
  data_type: string
  cluster: common
- name: create_user
  data_type: string
  cluster: common
- name: create_time
  data_type: temporal
  cluster: common
- name: update_by
  data_type: string
  cluster: common
- name: update_user
  data_type: string
  cluster: common
- name: update_time
  data_type: temporal
  cluster: common
- name: act_procinst_id
  data_type: string
  cluster: act_procinst
- name: app_tenant_code
  data_type: string
  cluster: tenant
- name: db_tenant_code
  data_type: string
  cluster: tenant
- name: act_procinst_no
  data_type: string
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  cluster: act_procinst
- name: organization_id
  data_type: string
  cluster: reference
- name: ref_cust_company_info
  data_type: string
  cluster: reference
- name: certification_type
  data_type: string
  cluster: certification
  dictionary: cust_certification_info__certification_type
- name: auto_verify_status
  data_type: string
  cluster: auto_verify
  dictionary: cust_certification_info__auto_verify_status
- name: auto_verify_msg
  data_type: string
  cluster: auto_verify
- name: auto_verify_time
  data_type: temporal
  cluster: auto_verify
- name: auto_verify_count
  data_type: number
  cluster: auto_verify
- name: auto_verify_data
  data_type: string
  cluster: auto_verify
- name: manual_verify_status
  data_type: string
  cluster: manual_verify
  dictionary: cust_certification_info__manual_verify_status
- name: manual_verify_msg
  data_type: string
  cluster: manual_verify
- name: manual_verify_time
  data_type: temporal
  cluster: manual_verify
- name: manual_verify_count
  data_type: number
  cluster: manual_verify
- name: face_business_no
  data_type: string
  cluster: certification
- name: verify_score
  data_type: number
  cluster: certification
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_certification_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_certification_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_certification_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
overlap:
  probed: true
  ratio: 0.0
  sample_size: 104
  miss: 104
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_certification_info__enable]]（`cust_certification_info.enable`）
- [[dicts/cust_certification_info__certification_type]]（`cust_certification_info.certification_type`）
- [[dicts/cust_certification_info__auto_verify_status]]（`cust_certification_info.auto_verify_status`）
- [[dicts/cust_certification_info__manual_verify_status]]（`cust_certification_info.manual_verify_status`）
