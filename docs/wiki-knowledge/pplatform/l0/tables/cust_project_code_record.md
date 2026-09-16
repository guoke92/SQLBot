---
type: table
title: 企业项目码输入记录
page_key: cust_project_code_record
belong: tables
status: draft
aliases: []
anchors:
- cust_project_code_record
sources:
- database_schema:lowcode_pplatform.cust_project_code_record
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 企业项目码输入记录

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### enterprise

`company_id`, `company_type`, `organization_id`

### project_code

`name`, `type`

### record_state

`status`, `remark`

### procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`use_id`, `channel_code`

## 字段

```ground:table
table: cust_project_code_record
database: lowcode_pplatform
description: 企业项目码输入记录
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- channel_code
clusters:
- key: common
  title: 通用（主键/编码/开关/审计/时间戳）
  include: always
- key: enterprise
  title: 企业主体与角色
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: project_code
  title: 项目码内容
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: record_state
  title: 记录状态与备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: procinst
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
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
  cluster: project_code
- name: company_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: enterprise
- name: use_id
  data_type: number
  description: 用户id
  nullable: true
- name: channel_code
  data_type: string
  description: 渠道码
  nullable: true
- name: status
  data_type: string
  description: 是否正确状态
  nullable: true
  cluster: record_state
  dictionary: cust_project_code_record_status
- name: company_type
  data_type: string
  description: 企业角色
  nullable: true
  cluster: enterprise
- name: type
  data_type: string
  description: 类型
  nullable: true
  cluster: project_code
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: record_state
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
  cluster: procinst
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
  cluster: procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: procinst
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: enterprise
```
