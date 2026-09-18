---
type: table
title: 推送企业的默认项目
page_key: cust_project_pushcust
belong: tables
status: draft
anchors: [cust_project_pushcust]
sources: ['database_schema:lowcode_pplatform.cust_project_pushcust']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_project_pushcust__source_sso_channel, cust_project_pushcust__enable]
---

# 推送企业的默认项目

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`

### sso_channel

`source_sso_channel`, `target_sso_channel`

### tenant

`app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### audit

（空）

### 未归簇

`project_id`, `organization_id`

## 字段

```ground:table
table: cust_project_pushcust
database: lowcode_pplatform
description: 推送企业的默认项目
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 主档身份
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
- key: sso_channel
  title: SSO渠道
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
- key: tenant
  title: 租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_pushcust
- key: audit
  title: 审计信息
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: identity
- name: source_sso_channel
  data_type: string
  description: 起始系统的SSO渠道
  cluster: sso_channel
  dictionary: cust_project_pushcust__source_sso_channel
- name: target_sso_channel
  data_type: string
  description: 跳转系统的SSO渠道
  cluster: sso_channel
- name: project_id
  data_type: string
  description: 项目id
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_project_pushcust__enable
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
  cluster: approval
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
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
```

## 页面链接

### 字典

- [[dicts/cust_project_pushcust__source_sso_channel]]（`cust_project_pushcust.source_sso_channel`）
- [[dicts/cust_project_pushcust__enable]]（`cust_project_pushcust.enable`）
