---
type: table
title: 问卷星白名单企业
page_key: cust_company_survey_whitelist
belong: tables
status: draft
aliases: []
anchors:
- cust_company_survey_whitelist
sources:
- database_schema:lowcode_pplatform.cust_company_survey_whitelist
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 问卷星白名单企业

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### company

`company_id`, `company_name`

### record_identity

`name`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`remark`, `organization_id`

## 字段

```ground:table
table: cust_company_survey_whitelist
database: lowcode_pplatform
description: 问卷星白名单企业
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- company_name
- code
- name
clusters:
- key: common
  title: 通用/审计字段
  include: always
- key: company
  title: 企业信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
- key: record_identity
  title: 白名单记录编码与名称
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
- key: act_procinst
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_whitelist
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: company_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: company
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: record_identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
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
  cluster: act_procinst
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
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
```
