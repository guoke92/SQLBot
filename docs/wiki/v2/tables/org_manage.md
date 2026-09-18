---
type: table
title: 机构管理
page_key: org_manage
belong: tables
status: draft
anchors: [org_manage]
sources: ['database_schema:lowcode_pplatform.org_manage']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
---

# 机构管理

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`, `org_no`, `org_name`, `parent_code`, `organization_id`

### attribute

`org_level`, `org_type`, `status`, `client_type`

### audit

（空）

### tenant

`app_tenant_code`, `db_tenant_code`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: org_manage
database: lowcode_pplatform
description: 机构管理
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, org_name, parent_code]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 机构标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
- key: attribute
  title: 机构属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.org_manage
- key: act_procinst
  title: 审批流程
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: identity
- name: org_no
  data_type: string
  description: 机构号
  cluster: identity
- name: org_name
  data_type: string
  description: 机构名称
  cluster: identity
- name: org_level
  data_type: number
  description: 机构层级
  cluster: attribute
- name: org_type
  data_type: string
  description: 机构类型
  cluster: attribute
- name: status
  data_type: string
  description: 状态
  cluster: attribute
- name: client_type
  data_type: string
  description: 端类型
  cluster: attribute
- name: parent_code
  data_type: string
  description: 父机构编号
  cluster: identity
- name: enable
  data_type: string
  description: enable
  cluster: common
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
  cluster: act_procinst
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
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: identity
```
