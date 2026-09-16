---
type: table
title: 租户产品菜单按钮表
page_key: tenant_product_menu_res
belong: tables
status: draft
aliases: []
anchors:
- tenant_product_menu_res
sources:
- database_schema:lowcode_pplatform.tenant_product_menu_res
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户产品菜单按钮表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_scope

`company_type`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### menu_resource

`product_code`, `menu_id`, `resource_id`, `name`

## 字段

```ground:table
table: tenant_product_menu_res
database: lowcode_pplatform
description: 租户产品菜单按钮表
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
- key: act_procinst
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product_menu_res
- key: tenant_scope
  title: 租户与组织
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product_menu_res
- key: menu_resource
  title: 产品菜单按钮
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product_menu_res
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: product_code
  data_type: string
  description: 产品code
  nullable: true
  cluster: menu_resource
- name: company_type
  data_type: string
  description: 企业类型
  nullable: true
  cluster: tenant_scope
  dictionary: tenant_product_menu_res_company_type
- name: menu_id
  data_type: number
  description: 菜单ID
  nullable: true
  cluster: menu_resource
- name: resource_id
  data_type: number
  description: 按钮ID
  nullable: true
  cluster: menu_resource
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: menu_resource
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_product_menu_res_enable
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
  cluster: tenant_scope
```
