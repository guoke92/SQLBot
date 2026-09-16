---
type: table
title: CA服务费项目配置
page_key: ca_fee_project_config
belong: tables
status: draft
aliases: []
anchors:
- ca_fee_project_config
sources:
- database_schema:lowcode_pplatform.ca_fee_project_config
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# CA服务费项目配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### fee_rule

`charge_enabled`, `supplier_annual_fee`, `core_annual_fee`, `pay_channel`, `special_company_list`, `block_scene_list`, `agreement_version`, `last_toggle_time`

### tenant_scope

`tenant_id`, `app_tenant_code`, `db_tenant_code`

### owner

`project_id`, `name`, `organization_id`

### approval_process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: ca_fee_project_config
database: lowcode_pplatform
description: CA服务费项目配置
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
- key: fee_rule
  title: 收费规则配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
- key: tenant_scope
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
- key: owner
  title: 归属对象
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
- key: approval_process
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: project_id
  data_type: number
  description: 项目ID
  nullable: true
  cluster: owner
- name: tenant_id
  data_type: number
  description: 所属租户
  nullable: true
  cluster: tenant_scope
- name: charge_enabled
  data_type: string
  description: 是否开启CA收费
  nullable: true
  cluster: fee_rule
  dictionary: ca_fee_project_config_charge_enabled
- name: supplier_annual_fee
  data_type: number
  description: 供应商角色年费（元）
  nullable: true
  cluster: fee_rule
- name: core_annual_fee
  data_type: number
  description: 核心企业角色年费（元）
  nullable: true
  cluster: fee_rule
- name: pay_channel
  data_type: string
  description: 缴费渠道JSON数组
  nullable: true
  cluster: fee_rule
- name: special_company_list
  data_type: string
  description: 特殊企业配置JSON数组
  nullable: true
  cluster: fee_rule
- name: block_scene_list
  data_type: string
  description: 拦截场景编码 JSON 数组，元素见 CaFeeInterceptSceneEnum
  nullable: true
  cluster: fee_rule
- name: agreement_version
  data_type: string
  description: 当前绑定收费协议版本号
  nullable: true
  cluster: fee_rule
- name: last_toggle_time
  data_type: temporal
  description: 最近一次收费开关切换时间
  nullable: true
  cluster: fee_rule
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: owner
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: ca_fee_project_config_enable
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
  cluster: tenant_scope
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_scope
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
  cluster: owner
```
