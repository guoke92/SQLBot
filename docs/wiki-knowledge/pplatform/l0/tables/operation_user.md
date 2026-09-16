---
type: table
title: 运营中台人员数据
page_key: operation_user
belong: tables
status: draft
aliases: []
anchors:
- operation_user
sources:
- database_schema:lowcode_pplatform.operation_user
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 运营中台人员数据

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `deleted`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### operation_identity

`operation_id`, `status`, `operation_group`, `operation_name`, `name`, `organization_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`remark`

## 字段

```ground:table
table: operation_user
database: lowcode_pplatform
description: 运营中台人员数据
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- operation_name
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: operation_identity
  title: 运营人员身份
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.operation_user
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.operation_user
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.operation_user
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: operation_id
  data_type: string
  description: 运营中台id
  nullable: true
  cluster: operation_identity
- name: status
  data_type: string
  description: 用户状态标识
  nullable: true
  cluster: operation_identity
- name: operation_group
  data_type: string
  description: 运营组别
  nullable: true
  cluster: operation_identity
- name: deleted
  data_type: string
  description: 删除标识
  nullable: true
  cluster: common
  dictionary: operation_user_deleted
- name: operation_name
  data_type: string
  description: 运营人员姓名
  nullable: true
  cluster: operation_identity
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: operation_identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: operation_user_enable
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
  cluster: operation_identity
```
