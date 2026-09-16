---
type: table
title: 客户操作运营变更记录
page_key: cust_oper_change_record
belong: tables
status: draft
aliases: []
anchors:
- cust_oper_change_record
sources:
- database_schema:lowcode_pplatform.cust_oper_change_record
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户操作运营变更记录

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### company

`company_id`, `company_name`, `company_code`

### person

`person_id`, `person_name`

### operator_change

`before_operator_id`, `before_operator_name`, `after_operator_id`, `after_operator_name`

### change_info

`change_type`, `change_reason`

### asset

`asset_id`, `asset_no`

### approval_process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`source_system`, `organization_id`

## 字段

```ground:table
table: cust_oper_change_record
database: lowcode_pplatform
description: 客户操作运营变更记录
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- person_name
- company_name
- company_code
- before_operator_name
- after_operator_name
- code
- name
clusters:
- key: common
  title: 通用与审计字段
  include: always
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: company
  title: 企业信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: person
  title: 企业联系人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: operator_change
  title: 运营人员变更前后
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: change_info
  title: 变更信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: asset
  title: 资产信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_oper_change_record
- key: approval_process
  title: 审批流程
  confidence: proposed
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
  nullable: true
  cluster: person
- name: person_name
  data_type: string
  description: 联系人姓名
  nullable: true
  cluster: person
- name: company_id
  data_type: number
  description: 企业ID
  nullable: true
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: company
- name: company_code
  data_type: string
  description: 企业编号
  nullable: true
  cluster: company
- name: before_operator_id
  data_type: string
  description: 变更前运营人员ID
  nullable: true
  cluster: operator_change
- name: before_operator_name
  data_type: string
  description: 变更前运营人员姓名
  nullable: true
  cluster: operator_change
- name: after_operator_id
  data_type: string
  description: 变更后运营人员ID
  nullable: true
  cluster: operator_change
- name: after_operator_name
  data_type: string
  description: 变更后运营人员姓名
  nullable: true
  cluster: operator_change
- name: change_type
  data_type: string
  description: 变更类型
  nullable: true
  cluster: change_info
  dictionary: cust_oper_change_record_change_type
- name: change_reason
  data_type: string
  description: 变更原因
  nullable: true
  cluster: change_info
- name: asset_id
  data_type: string
  description: 资产id
  nullable: true
  cluster: asset
- name: asset_no
  data_type: string
  description: 资产编号
  nullable: true
  cluster: asset
- name: source_system
  data_type: string
  description: 来源系统
  nullable: true
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: common
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_oper_change_record_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: approval_process
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval_process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_process
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
```
