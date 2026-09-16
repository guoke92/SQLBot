---
type: table
title: 资方规则信息详情
page_key: funding_rule_detail
belong: tables
status: draft
aliases: []
anchors:
- funding_rule_detail
sources:
- database_schema:lowcode_pplatform.funding_rule_detail
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 资方规则信息详情

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### rule

`rule_value`, `fund_rule_code_ref`, `rule_key`, `rule_layer`, `version`, `rule_info_id`

### funding_product

`funding_party_mark`, `product_code`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### org_check

`organization_id`, `check_scene`

### tenant

`app_tenant_code`, `db_tenant_code`

### basic

`name`, `remark`

## 字段

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
description: 资方规则信息详情
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- product_code
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: rule
  title: 规则项
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: funding_product
  title: 资方与产品
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: org_check
  title: 机构与校验
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: basic
  title: 基础信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: rule_value
  data_type: string
  description: 规则值
  nullable: true
  cluster: rule
- name: fund_rule_code_ref
  data_type: string
  description: 关联规则信息code
  nullable: true
  cluster: rule
- name: rule_key
  data_type: string
  description: 字段key 对应front_key
  nullable: true
  cluster: rule
- name: rule_layer
  data_type: string
  description: 规则层
  nullable: true
  cluster: rule
  dictionary: funding_rule_detail_rule_layer
- name: version
  data_type: number
  description: 版本
  nullable: true
  cluster: rule
- name: funding_party_mark
  data_type: string
  description: 资方标识
  nullable: true
  cluster: funding_product
- name: product_code
  data_type: string
  description: 产品code
  nullable: true
  cluster: funding_product
- name: rule_info_id
  data_type: number
  description: 关系规则信息ID
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
  cluster: basic
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: funding_rule_detail_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: basic
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
  cluster: org_check
- name: check_scene
  data_type: string
  description: 校验场景
  nullable: true
  cluster: org_check
  dictionary: funding_rule_detail_check_scene
```
