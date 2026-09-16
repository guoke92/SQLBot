---
type: table
title: 租户项目审批流程文件表
page_key: tenant_project_approval_flow_file
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_file
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_file
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批流程文件表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### file_info

`file_id`, `file_name`, `file_url`, `file_path`

### category

`catg_id`, `catg_name`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### relation

`busi_key`, `ref_tenant_project_approval_flow_file_project_approval_flow_node`, `ref_tenant_project_approval_flow_file_comment`, `ref_tenant_project_approval_flow_file_project_approval`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_file
database: lowcode_pplatform
description: 租户项目审批流程文件表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- catg_name
- file_name
- code
- name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: file_info
  title: 文件信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: category
  title: 影像分类
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: approval_flow
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: relation
  title: 业务关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: tenant_org
  title: 租户与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: catg_id
  data_type: string
  description: 影像分类编码
  nullable: true
  cluster: category
  dictionary: tenant_project_approval_flow_file_catg_id
- name: catg_name
  data_type: string
  description: 影像分类名称
  nullable: true
  cluster: category
- name: busi_key
  data_type: string
  description: 业务key
  nullable: true
  cluster: relation
- name: file_id
  data_type: string
  description: 文件id
  nullable: true
  cluster: file_info
- name: file_name
  data_type: string
  description: 文件名称
  nullable: true
  cluster: file_info
- name: file_url
  data_type: string
  description: 文件url
  nullable: true
  cluster: file_info
- name: file_path
  data_type: string
  description: 文件路径
  nullable: true
  cluster: file_info
- name: ref_tenant_project_approval_flow_file_project_approval_flow_node
  data_type: string
  description: 关联项目流程节点
  nullable: true
  cluster: relation
- name: ref_tenant_project_approval_flow_file_comment
  data_type: string
  description: 关联项目审批
  nullable: true
  cluster: relation
- name: ref_tenant_project_approval_flow_file_project_approval
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
  cluster: common
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_project_approval_flow_file_enable
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_org
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_org
```
