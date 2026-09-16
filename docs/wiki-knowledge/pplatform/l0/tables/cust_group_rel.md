---
type: table
title: 集团成员单位关系表
page_key: cust_group_rel
belong: tables
status: draft
aliases: []
anchors:
- cust_group_rel
sources:
- database_schema:lowcode_pplatform.cust_group_rel
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 集团成员单位关系表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### member

`cust_id`, `cust_type`, `status`, `organization_id`

### group_hierarchy

`parent_group_id`, `parent_cust_id`, `root_cust_id`, `root_group_id`, `root_flag`, `level`

### approval_process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: cust_group_rel
database: lowcode_pplatform
description: 集团成员单位关系表
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
- key: member
  title: 成员企业信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: group_hierarchy
  title: 集团层级关系
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: approval_process
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: cust_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: member
- name: parent_group_id
  data_type: number
  description: 父id
  nullable: true
  cluster: group_hierarchy
- name: parent_cust_id
  data_type: number
  description: 父企业id
  nullable: true
  cluster: group_hierarchy
- name: root_cust_id
  data_type: number
  description: 根企业id
  nullable: true
  cluster: group_hierarchy
- name: root_group_id
  data_type: number
  description: 根id
  nullable: true
  cluster: group_hierarchy
- name: root_flag
  data_type: string
  description: 是否集团企业 Y:是 N:不是
  nullable: true
  cluster: group_hierarchy
  dictionary: cust_group_rel_root_flag
- name: level
  data_type: number
  description: 层级
  nullable: true
  cluster: group_hierarchy
- name: cust_type
  data_type: string
  description: 企业角色 多企业角色用逗号分隔
  nullable: true
  cluster: member
- name: status
  data_type: string
  description: 状态 已生效:EFFECTIVE 未生效:INEFFECTIVE 已拒绝:REJECTED
  nullable: true
  cluster: member
  dictionary: cust_group_rel_status
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: common
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_group_rel_enable
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
  cluster: approval_process
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
  cluster: approval_process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_process
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: member
```
