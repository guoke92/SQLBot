---
type: table
title: 客户操作运营变更记录
page_key: cust_oper_change_record
belong: tables
status: draft
anchors: [cust_oper_change_record]
sources: ['database_schema:lowcode_pplatform.cust_oper_change_record']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_person_info, cust_company_info, cust_oper_change_record__change_type,
  cust_oper_change_record__enable]
---

# 客户操作运营变更记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### tenant_source

`source_system`, `app_tenant_code`, `db_tenant_code`

### customer_subject

`person_id`, `person_name`, `company_id`, `company_name`, `company_code`, `organization_id`

### oper_change

`before_operator_id`, `before_operator_name`, `after_operator_id`, `after_operator_name`, `change_type`, `change_reason`

### asset

`asset_id`, `asset_no`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: cust_oper_change_record
database: lowcode_pplatform
description: 客户操作运营变更记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [person_name, company_name, before_operator_name, after_operator_name,
  code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: tenant_source
  title: 租户与来源
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: customer_subject
  title: 客户企业与联系人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: oper_change
  title: 运营人员变更
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: asset
  title: 资产信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: person_id
  data_type: number
  description: 企业联系人id
  cluster: customer_subject
- name: person_name
  data_type: string
  description: 联系人姓名
  cluster: customer_subject
- name: company_id
  data_type: number
  description: 企业ID
  cluster: customer_subject
- name: company_name
  data_type: string
  description: 企业名称
  cluster: customer_subject
- name: company_code
  data_type: string
  description: 企业编号
  cluster: customer_subject
- name: before_operator_id
  data_type: string
  description: 变更前运营人员ID
  cluster: oper_change
- name: before_operator_name
  data_type: string
  description: 变更前运营人员姓名
  cluster: oper_change
- name: after_operator_id
  data_type: string
  description: 变更后运营人员ID
  cluster: oper_change
- name: after_operator_name
  data_type: string
  description: 变更后运营人员姓名
  cluster: oper_change
- name: change_type
  data_type: string
  description: 变更类型
  cluster: oper_change
  dictionary: cust_oper_change_record__change_type
- name: change_reason
  data_type: string
  description: 变更原因
  cluster: oper_change
- name: asset_id
  data_type: string
  description: 资产id
  cluster: asset
- name: asset_no
  data_type: string
  description: 资产编号
  cluster: asset
- name: source_system
  data_type: string
  description: 来源系统
  cluster: tenant_source
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_oper_change_record__enable
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_source
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_source
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: customer_subject
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_person_info.id
right: cust_oper_change_record.person_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_oper_change_record.person_id;database_profile:lowcode_pplatform.cust_oper_change_record.person_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: person
  comment: 企业联系人id
overlap:
  probed: true
  ratio: 0.9947
  sample_size: 190
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_oper_change_record.company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_oper_change_record.company_id;database_profile:lowcode_pplatform.cust_oper_change_record.company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业ID
overlap:
  probed: true
  ratio: 1.0
  sample_size: 97
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_oper_change_record.company_code
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_oper_change_record.company_code;database_profile:lowcode_pplatform.cust_oper_change_record.company_code
source: name
join_role: business_code
priority: secondary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业编号
overlap:
  probed: true
  ratio: 1.0
  sample_size: 97
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/cust_person_info]]
- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_oper_change_record__change_type]]（`cust_oper_change_record.change_type`）
- [[dicts/cust_oper_change_record__enable]]（`cust_oper_change_record.enable`）
