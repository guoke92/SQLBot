---
type: table
title: 资方规则信息
page_key: funding_rule_info
belong: tables
status: draft
aliases: []
anchors:
- funding_rule_info
sources:
- database_schema:lowcode_pplatform.funding_rule_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 资方规则信息

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### funding

`funding_party_mark`, `funding_party_name`, `organization_id`

### rule

`rule_status`, `version`, `name`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`product_code`, `remark`

## 字段

```ground:table
table: funding_rule_info
database: lowcode_pplatform
description: 资方规则信息
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- funding_party_name
- product_code
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: funding
  title: 资方/机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_info
- key: rule
  title: 规则
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_info
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_info
- key: tenant
  title: 租户
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: funding_party_mark
  data_type: string
  description: 资金方标识
  nullable: true
  cluster: funding
- name: funding_party_name
  data_type: string
  description: 资方名称
  nullable: true
  cluster: funding
- name: product_code
  data_type: string
  description: 产品code
  nullable: true
- name: rule_status
  data_type: string
  description: 规则状态 ACTIVE/INACTIVE/PENDING
  nullable: true
  cluster: rule
  dictionary: funding_rule_info_rule_status
- name: version
  data_type: number
  description: 版本号
  nullable: true
  cluster: rule
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: rule
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: funding_rule_info_enable
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
  cluster: approval
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
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: funding
```
