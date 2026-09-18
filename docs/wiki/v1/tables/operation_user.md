---
type: table
title: 运营中台人员数据
page_key: operation_user
belong: tables
status: draft
anchors: [operation_user]
sources: ['database_schema:lowcode_pplatform.operation_user']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [operation_user__deleted, operation_user__enable, operation_user__db_tenant_code]
---

# 运营中台人员数据

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `deleted`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### operation

`operation_id`, `status`, `operation_group`, `operation_name`, `organization_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: operation_user
database: lowcode_pplatform
description: 运营中台人员数据
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [operation_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: operation
  title: 运营人员信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.operation_user
- key: workflow
  title: 审批流程信息
  trust: proposed
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
  cluster: operation
- name: status
  data_type: string
  description: 用户状态标识
  cluster: operation
- name: operation_group
  data_type: string
  description: 运营组别
  cluster: operation
- name: deleted
  data_type: string
  description: 删除标识
  cluster: common
  dictionary: operation_user__deleted
- name: operation_name
  data_type: string
  description: 运营人员姓名
  cluster: operation
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
  dictionary: operation_user__enable
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
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
  dictionary: operation_user__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: operation
```

## 页面链接

### 字典

- [[dicts/operation_user__deleted]]（`operation_user.deleted`）
- [[dicts/operation_user__enable]]（`operation_user.enable`）
- [[dicts/operation_user__db_tenant_code]]（`operation_user.db_tenant_code`）
