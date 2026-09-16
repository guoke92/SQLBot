---
type: table
title: 用户企业角色
page_key: cust_user_rel
belong: tables
status: draft
aliases: []
anchors:
- cust_user_rel
sources:
- database_schema:lowcode_pplatform.cust_user_rel
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 用户企业角色

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### user

`user_id`, `user_type`

### company

`company_id`, `company_name`, `company_type`

### role

`name`, `type_status`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: cust_user_rel
database: lowcode_pplatform
description: 用户企业角色
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- company_name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: user
  title: 用户
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: company
  title: 企业
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: role
  title: 角色/关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: process
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: tenant
  title: 租户
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
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
  cluster: role
- name: user_id
  data_type: number
  description: 用户id
  nullable: true
  cluster: user
- name: company_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: company
- name: company_type
  data_type: string
  description: 企业类型
  nullable: true
  cluster: company
- name: type_status
  data_type: string
  description: 客户角色
  nullable: true
  cluster: role
  dictionary: cust_user_rel_type_status
- name: user_type
  data_type: string
  description: 联系人类型
  nullable: true
  cluster: user
  dictionary: cust_user_rel_user_type
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_user_rel_enable
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
  cluster: process
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
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
```
