---
type: table
title: 客户快捷入口配置
page_key: cust_customized_product
belong: tables
status: draft
aliases: []
anchors:
- cust_customized_product
sources:
- database_schema:lowcode_pplatform.cust_customized_product
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户快捷入口配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### entry_config

`name`, `url`, `logo_icon_url`, `view_order`, `remark`

### relation

`cust_id`, `ref_cust_customized_product_cust_company_info`, `organization_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: cust_customized_product
database: lowcode_pplatform
description: 客户快捷入口配置
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
- key: entry_config
  title: 快捷入口展示配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
- key: relation
  title: 客户与机构关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
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
  description: 产品名称
  nullable: true
  cluster: entry_config
- name: cust_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: relation
- name: url
  data_type: string
  description: 跳转链接
  nullable: true
  cluster: entry_config
- name: logo_icon_url
  data_type: string
  description: 图标
  nullable: true
  cluster: entry_config
- name: view_order
  data_type: number
  description: 显示顺序
  nullable: true
  cluster: entry_config
- name: ref_cust_customized_product_cust_company_info
  data_type: string
  description: 客户关联自定义产品配置
  nullable: true
  cluster: relation
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: entry_config
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
  cluster: relation
```
