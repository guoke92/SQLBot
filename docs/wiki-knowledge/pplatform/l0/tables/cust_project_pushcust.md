---
type: table
title: 推送企业的默认项目
page_key: cust_project_pushcust
belong: tables
status: draft
aliases: []
anchors:
- cust_project_pushcust
sources:
- database_schema:lowcode_pplatform.cust_project_pushcust
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 推送企业的默认项目

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### sso

`source_sso_channel`, `target_sso_channel`

### association

`project_id`, `organization_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`name`, `remark`

## 字段

```ground:table
table: cust_project_pushcust
database: lowcode_pplatform
description: 推送企业的默认项目
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
- key: sso
  title: SSO渠道
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
- key: association
  title: 业务关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
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
- name: source_sso_channel
  data_type: string
  description: 起始系统的SSO渠道
  nullable: true
  cluster: sso
- name: target_sso_channel
  data_type: string
  description: 跳转系统的SSO渠道
  nullable: true
  cluster: sso
- name: project_id
  data_type: string
  description: 项目id
  nullable: true
  cluster: association
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_project_pushcust_enable
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
  cluster: association
```
