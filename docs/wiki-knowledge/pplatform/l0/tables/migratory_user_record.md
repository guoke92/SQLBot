---
type: table
title: 迁移用户记录表
page_key: migratory_user_record
belong: tables
status: draft
aliases: []
anchors:
- migratory_user_record
sources:
- database_schema:lowcode_pplatform.migratory_user_record
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 迁移用户记录表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### user_profile

`name`, `user_id`, `is_login`

### approval_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`remark`, `organization_id`

## 字段

```ground:table
table: migratory_user_record
database: lowcode_pplatform
description: 迁移用户记录表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: user_profile
  title: 迁移用户身份与登录
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.migratory_user_record
- key: approval_procinst
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.migratory_user_record
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.migratory_user_record
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
  cluster: user_profile
- name: user_id
  data_type: number
  description: 迁移用户id
  nullable: true
  cluster: user_profile
- name: is_login
  data_type: string
  description: 是否登录过
  nullable: true
  cluster: user_profile
  dictionary: migratory_user_record_is_login
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: migratory_user_record_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
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
  cluster: approval_procinst
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
  cluster: approval_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
```
