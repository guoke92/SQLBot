---
type: table
title: 资方规则前端配置页面
page_key: funding_rule_front_cfg
belong: tables
status: draft
aliases: []
anchors:
- funding_rule_front_cfg
sources:
- database_schema:lowcode_pplatform.funding_rule_front_cfg
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 资方规则前端配置页面

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### front

`front_key_name`, `front_key`, `front_field_style`

### rule

`rule_layer`, `key_name`, `key_type`, `rule_key`, `check_scene`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### product

`product_code`, `name`

### 未归簇

`organization_id`

## 字段

```ground:table
table: funding_rule_front_cfg
database: lowcode_pplatform
description: 资方规则前端配置页面
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- product_code
- front_key_name
- key_name
- code
- name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: tenant
  title: 租户隔离
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: front
  title: 前端展示配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: rule
  title: 规则定义与校验
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: act_procinst
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: product
  title: 产品维度
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: rule_layer
  data_type: string
  description: 规则层 UNDERLYING/FINANCING
  nullable: true
  cluster: rule
  dictionary: funding_rule_front_cfg_rule_layer
- name: product_code
  data_type: string
  description: 产品code
  nullable: true
  cluster: product
- name: front_key_name
  data_type: string
  description: 前端展示字段名称
  nullable: true
  cluster: front
- name: front_key
  data_type: string
  description: 前端字段key
  nullable: true
  cluster: front
- name: front_field_style
  data_type: string
  description: 前端字段渲染json
  nullable: true
  cluster: front
- name: key_name
  data_type: string
  description: 字段名称描述
  nullable: true
  cluster: rule
- name: key_type
  data_type: string
  description: 字段业务规则类型
  nullable: true
  cluster: rule
  dictionary: funding_rule_front_cfg_key_type
- name: rule_key
  data_type: string
  description: 规则字段key
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
  cluster: product
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: funding_rule_front_cfg_enable
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
- name: check_scene
  data_type: string
  description: 校验场景
  nullable: true
  cluster: rule
  dictionary: funding_rule_front_cfg_check_scene
```
