---
type: table
title: 项目运营文件管理
page_key: project_file_info
belong: tables
status: draft
aliases: []
anchors:
- project_file_info
sources:
- database_schema:lowcode_pplatform.project_file_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 项目运营文件管理

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### file_content

`title`, `content`, `file_type`, `name`, `remark`

### relation

`project_id`, `organization_id`

## 字段

```ground:table
table: project_file_info
database: lowcode_pplatform
description: 项目运营文件管理
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- title
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: flow
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
- key: file_content
  title: 文件内容信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
- key: relation
  title: 归属关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.project_file_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: title
  data_type: string
  description: 标题
  nullable: true
  cluster: file_content
- name: content
  data_type: string
  description: 描述
  nullable: true
  cluster: file_content
- name: file_type
  data_type: string
  description: 文件模块类型
  nullable: true
  cluster: file_content
  dictionary: project_file_info_file_type
- name: project_id
  data_type: number
  description: 关联项目ID
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
  cluster: file_content
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: file_content
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
  cluster: flow
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
  cluster: flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: relation
```
