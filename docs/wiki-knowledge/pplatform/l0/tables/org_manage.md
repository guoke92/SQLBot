---
type: table
title: 机构管理
page_key: org_manage
belong: tables
status: draft
aliases: []
anchors:
- org_manage
sources:
- database_schema:lowcode_pplatform.org_manage
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 机构管理

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### org_identity

`name`, `org_no`, `org_name`, `organization_id`

### org_attr

`org_level`, `org_type`, `status`, `client_type`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`parent_code`, `remark`

## 字段

```ground:table
table: org_manage
database: lowcode_pplatform
description: 机构管理
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- org_name
- parent_code
clusters:
- key: common
  title: 通用/审计
  include: always
- key: org_identity
  title: 机构身份标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
- key: org_attr
  title: 机构属性
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
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
  cluster: org_identity
- name: org_no
  data_type: string
  description: 机构号
  nullable: true
  cluster: org_identity
- name: org_name
  data_type: string
  description: 机构名称
  nullable: true
  cluster: org_identity
- name: org_level
  data_type: number
  description: 机构层级
  nullable: true
  cluster: org_attr
- name: org_type
  data_type: string
  description: 机构类型
  nullable: true
  cluster: org_attr
- name: status
  data_type: string
  description: 状态
  nullable: true
  cluster: org_attr
- name: client_type
  data_type: string
  description: 端类型
  nullable: true
  cluster: org_attr
- name: parent_code
  data_type: string
  description: 父机构编号
  nullable: true
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
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
  cluster: org_identity
```
