---
type: table
title: 租户项目审批流程表
page_key: tenant_project_approval_flow
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval_flow
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批流程表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### node

`node_code`, `node_name`, `node_order`, `node_status`

### approver

`approver_user_id`, `approver_user_name`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### flags

`is_optional`, `is_operate`

### basic

`name`, `remark`

### tenant

`app_tenant_code`, `db_tenant_code`

### relation

`ref_tenant_project_approval_flow_tenant_project_approval`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow
database: lowcode_pplatform
description: 租户项目审批流程表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- node_code
- node_name
- approver_user_name
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: node
  title: 审批节点
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: approver
  title: 审批人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: process
  title: 流程实例/申请
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: flags
  title: 节点开关标记
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: basic
  title: 基础名称与备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: relation
  title: 关联外键
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: node_code
  data_type: string
  description: 节点编码
  nullable: true
  cluster: node
  dictionary: tenant_project_approval_flow_node_code
- name: node_name
  data_type: string
  description: 节点名称（中文）
  nullable: true
  cluster: node
- name: node_order
  data_type: number
  description: 节点顺序，从 1 开始
  nullable: true
  cluster: node
- name: node_status
  data_type: string
  description: 节点状态
  nullable: true
  cluster: node
  dictionary: tenant_project_approval_flow_node_status
- name: is_optional
  data_type: string
  description: 是否可选节点：Y/N
  nullable: true
  cluster: flags
  dictionary: tenant_project_approval_flow_is_optional
- name: is_operate
  data_type: string
  description: 是否可编辑
  nullable: true
  cluster: flags
  dictionary: tenant_project_approval_flow_is_operate
- name: approver_user_id
  data_type: string
  description: 审批人 userId
  nullable: true
  cluster: approver
- name: approver_user_name
  data_type: string
  description: 审批人姓名
  nullable: true
  cluster: approver
- name: ref_tenant_project_approval_flow_tenant_project_approval
  data_type: string
  description: 关联项目审批
  nullable: true
  cluster: relation
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: basic
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: basic
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
  cluster: relation
```
