---
type: table
title: 迁移用户记录表
page_key: migratory_user_record
belong: tables
status: draft
anchors: [migratory_user_record]
sources: ['database_schema:lowcode_pplatform.migratory_user_record']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [migratory_user_record__is_login, migratory_user_record__enable]
---

# 迁移用户记录表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `is_login`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### tenant

`app_tenant_code`, `db_tenant_code`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### ownership

`user_id`, `organization_id`

## 字段

```ground:table
table: migratory_user_record
database: lowcode_pplatform
description: 迁移用户记录表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.migratory_user_record
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.migratory_user_record
- key: process
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.migratory_user_record
- key: ownership
  title: 归属对象
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: user_id
  data_type: number
  description: 迁移用户id
  cluster: ownership
- name: is_login
  data_type: string
  description: 是否登录过
  cluster: common
  dictionary: migratory_user_record__is_login
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: migratory_user_record__enable
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
  cluster: ownership
```

## 页面链接

### 字典

- [[dicts/migratory_user_record__is_login]]（`migratory_user_record.is_login`）
- [[dicts/migratory_user_record__enable]]（`migratory_user_record.enable`）
