---
type: table
title: 授权确认书表
page_key: authorization_agreement
belong: tables
status: draft
aliases: []
anchors:
- authorization_agreement
sources:
- database_schema:lowcode_pplatform.authorization_agreement
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 授权确认书表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### cust

`cust_manager_id`, `cust_id`, `original_cust_id`, `cust_manager_name`, `cust_name`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### agreement

`name`, `platform_product_code`, `authed_status`, `company_type`, `remark`, `organization_id`, `creation_type`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: authorization_agreement
database: lowcode_pplatform
description: 授权确认书表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- platform_product_code
- cust_manager_name
- cust_name
clusters:
- key: common
  title: 通用/审计字段
  include: always
- key: cust
  title: 企业主档信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
- key: act_procinst
  title: 审批流程信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
- key: agreement
  title: 授权书业务属性
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
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
  cluster: agreement
- name: cust_manager_id
  data_type: number
  description: 企业管理员id
  nullable: true
  cluster: cust
- name: platform_product_code
  data_type: string
  description: 平台产品id
  nullable: true
  cluster: agreement
  dictionary: authorization_agreement_platform_product_code
- name: authed_status
  data_type: string
  description: 授权书认证状态
  nullable: true
  cluster: agreement
  dictionary: authorization_agreement_authed_status
- name: cust_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: cust
- name: original_cust_id
  data_type: string
  description: 源系统custid
  nullable: true
  cluster: cust
- name: company_type
  data_type: string
  description: 企业角色
  nullable: true
  cluster: agreement
  dictionary: authorization_agreement_company_type
- name: cust_manager_name
  data_type: string
  description: 客户管理员名称
  nullable: true
  cluster: cust
- name: cust_name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: cust
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: authorization_agreement_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: agreement
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
  cluster: agreement
- name: creation_type
  data_type: string
  description: 创建类型
  nullable: true
  cluster: agreement
  dictionary: authorization_agreement_creation_type
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: authorization_agreement.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.authorization_agreement.platform_product_code
```
