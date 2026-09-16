---
type: table
title: 客户产品角色关联表
page_key: cust_role_info
belong: tables
status: draft
aliases: []
anchors:
- cust_role_info
sources:
- database_schema:lowcode_pplatform.cust_role_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户产品角色关联表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### role_profile

`name`, `remark`, `status`, `role_type`

### approval_proc

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### cust_ref

`organization_id`, `platform_cust_id`, `ref_cust_company_info`, `ref_cust_auth_application`, `main_data_id`

## 字段

```ground:table
table: cust_role_info
database: lowcode_pplatform
description: 客户产品角色关联表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: role_profile
  title: 角色主档属性
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: approval_proc
  title: 流程审批信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: cust_ref
  title: 客户/主数据关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: role_profile
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_role_info_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: role_profile
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
  cluster: approval_proc
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
  cluster: approval_proc
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_proc
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_proc
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: cust_ref
- name: status
  data_type: string
  description: 状态
  nullable: true
  cluster: role_profile
  dictionary: cust_role_info_status
- name: platform_cust_id
  data_type: number
  description: 关联平台企业ID
  nullable: true
  cluster: cust_ref
- name: ref_cust_company_info
  data_type: string
  description: 客户类型
  nullable: true
  cluster: cust_ref
- name: ref_cust_auth_application
  data_type: string
  description: 应用客户角色
  nullable: true
  cluster: cust_ref
- name: role_type
  data_type: string
  description: 角色类型
  nullable: true
  cluster: role_profile
  dictionary: cust_role_info_role_type
- name: main_data_id
  data_type: number
  description: 主数据id
  nullable: true
  cluster: cust_ref
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_role_info.ref_cust_company_info
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_role_info.ref_cust_company_info
```

```ground:relation
type: EQUI_JOIN
left: cust_auth_application.id
right: cust_role_info.ref_cust_auth_application
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_role_info.ref_cust_auth_application
```
