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
  cust_oper_change_record__enable, cust_oper_change_record__app_tenant_code]
---

# 客户操作运营变更记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `source_system`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### person

`person_id`, `person_name`

### company

`company_id`, `company_name`, `company_code`

### change_operator

`before_operator_id`, `before_operator_name`, `after_operator_id`, `after_operator_name`

### change_info

`change_type`, `change_reason`

### asset

`asset_id`, `asset_no`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

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
- key: person
  title: 企业联系人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: company
  title: 企业主档
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: change_operator
  title: 运营人员变更
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: change_info
  title: 变更信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: asset
  title: 资产信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: process
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: tenant
  title: 租户隔离
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
  cluster: person
- name: person_name
  data_type: string
  description: 联系人姓名
  cluster: person
- name: company_id
  data_type: number
  description: 企业ID
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  cluster: company
- name: company_code
  data_type: string
  description: 企业编号
  cluster: company
- name: before_operator_id
  data_type: string
  description: 变更前运营人员ID
  cluster: change_operator
- name: before_operator_name
  data_type: string
  description: 变更前运营人员姓名
  cluster: change_operator
- name: after_operator_id
  data_type: string
  description: 变更后运营人员ID
  cluster: change_operator
- name: after_operator_name
  data_type: string
  description: 变更后运营人员姓名
  cluster: change_operator
- name: change_type
  data_type: string
  description: 变更类型
  cluster: change_info
  dictionary: cust_oper_change_record__change_type
- name: change_reason
  data_type: string
  description: 变更原因
  cluster: change_info
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
  cluster: common
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
  cluster: process
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
  dictionary: cust_oper_change_record__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
```

## 关联关系

### likely — 值域支持较强

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
  ratio: 0.9948
  sample_size: 191
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: family_suffix person，overlap 0.9948，likely 外键
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
  sample_size: 99
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: family_suffix company，overlap 1.0，likely 外键
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
  sample_size: 99
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: family_suffix company，overlap 1.0，码对码边；同表已有 company_id 指向父表主键，可作
  secondary
```

## 页面链接

### 关联表

- [[tables/cust_person_info]]
- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_oper_change_record__change_type]]（`cust_oper_change_record.change_type`）
- [[dicts/cust_oper_change_record__enable]]（`cust_oper_change_record.enable`）
- [[dicts/cust_oper_change_record__app_tenant_code]]（`cust_oper_change_record.app_tenant_code`）
