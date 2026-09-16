---
type: table
title: 企业生命周期记录
page_key: cust_company_lifecycle_info
belong: tables
status: draft
aliases: []
anchors:
- cust_company_lifecycle_info
sources:
- database_schema:lowcode_pplatform.cust_company_lifecycle_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 企业生命周期记录

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### lifecycle

`reason`, `attach`, `type`

### company_ref

`company_id`, `organization_id`, `ref_cust_company_info`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### misc

`name`, `remark`

## 字段

```ground:table
table: cust_company_lifecycle_info
database: lowcode_pplatform
description: 企业生命周期记录
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: lifecycle
  title: 生命周期动作
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
- key: company_ref
  title: 关联主体
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
- key: misc
  title: 名称与备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: company_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: company_ref
- name: reason
  data_type: string
  description: 冻结原因
  nullable: true
  cluster: lifecycle
- name: attach
  data_type: string
  description: 冻结附件路径集合
  nullable: true
  cluster: lifecycle
- name: type
  data_type: string
  description: 类型
  nullable: true
  cluster: lifecycle
  dictionary: cust_company_lifecycle_info_type
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: misc
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_company_lifecycle_info_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: misc
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
  cluster: workflow
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
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: company_ref
- name: ref_cust_company_info
  data_type: string
  description: 关联企业code
  nullable: true
  cluster: company_ref
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_lifecycle_info.ref_cust_company_info
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info.ref_cust_company_info
```
