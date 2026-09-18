---
type: table
title: 问卷星白名单企业
page_key: cust_company_survey_whitelist
belong: tables
status: draft
anchors: [cust_company_survey_whitelist]
sources: ['database_schema:lowcode_pplatform.cust_company_survey_whitelist']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_company_survey_whitelist__enable]
---

# 问卷星白名单企业

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### company

`company_id`, `company_name`

### whitelist_identity

`name`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: cust_company_survey_whitelist
database: lowcode_pplatform
description: 问卷星白名单企业
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [company_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: company
  title: 企业信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
- key: whitelist_identity
  title: 白名单标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
- key: tenant
  title: 租户隔离
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: company_id
  data_type: number
  description: 企业id
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  cluster: company
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: whitelist_identity
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_company_survey_whitelist__enable
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_survey_whitelist.company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist.company_id;database_profile:lowcode_pplatform.cust_company_survey_whitelist.company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 11
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_company_survey_whitelist__enable]]（`cust_company_survey_whitelist.enable`）
