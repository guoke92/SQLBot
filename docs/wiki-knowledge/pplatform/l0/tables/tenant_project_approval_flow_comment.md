---
type: table
title: 租户项目审批备注信息
page_key: tenant_project_approval_flow_comment
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_comment
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批备注信息

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### approval_flow

`ref_tenant_project_approval_flow_comment_approval`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### comment_body

`content`, `name`, `remark`

### participant

`cc_user_id`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_comment
database: lowcode_pplatform
description: 租户项目审批备注信息
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
- key: approval_flow
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: comment_body
  title: 备注正文
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: participant
  title: 参与人与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: content
  data_type: string
  description: 备注内容
  nullable: true
  cluster: comment_body
- name: cc_user_id
  data_type: string
  description: 抄送相关人员
  nullable: true
  cluster: participant
- name: ref_tenant_project_approval_flow_comment_approval
  data_type: string
  description: 关联项目审批
  nullable: true
  cluster: approval_flow
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: comment_body
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_project_approval_flow_comment_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: comment_body
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
  cluster: participant
```
