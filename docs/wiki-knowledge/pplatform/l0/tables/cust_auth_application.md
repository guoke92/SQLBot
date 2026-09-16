---
type: table
title: 客户产品开通表
page_key: cust_auth_application
belong: tables
status: draft
aliases: []
anchors:
- cust_auth_application
sources:
- database_schema:lowcode_pplatform.cust_auth_application
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户产品开通表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_info

`name`, `platform_product_code`, `application`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### opening

`open_status`, `open_time`

### relation

`organization_id`, `cust_manager_id`, `ref_cust_company_info`, `ref_parent_company`, `main_data_id`, `ref_cust_auth_application_tenant_product`

### 未归簇

`remark`

## 字段

```ground:table
table: cust_auth_application
database: lowcode_pplatform
description: 客户产品开通表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- platform_product_code
clusters:
- key: common
  title: 通用
  include: always
- key: product_info
  title: 产品信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: approval_flow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: opening
  title: 开通信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: relation
  title: 关联主体
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
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
  cluster: product_info
- name: platform_product_code
  data_type: string
  description: 平台产品编码
  nullable: true
  cluster: product_info
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_auth_application_enable
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
  cluster: approval_flow
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
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: relation
- name: application
  data_type: string
  description: 产品应用
  nullable: true
  cluster: product_info
- name: open_status
  data_type: string
  description: 开通状态
  nullable: true
  cluster: opening
  dictionary: cust_auth_application_open_status
- name: cust_manager_id
  data_type: number
  description: 企业管理员
  nullable: true
  cluster: relation
- name: open_time
  data_type: temporal
  description: 开通时间
  nullable: true
  cluster: opening
- name: ref_cust_company_info
  data_type: string
  description: 客户应用
  nullable: true
  cluster: relation
- name: ref_parent_company
  data_type: string
  description: 关联母公司
  nullable: true
  cluster: relation
- name: main_data_id
  data_type: number
  description: 主数据id
  nullable: true
  cluster: relation
- name: ref_cust_auth_application_tenant_product
  data_type: string
  description: 关联应用
  nullable: true
  cluster: relation
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: cust_auth_application.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_auth_application.platform_product_code
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_auth_application.ref_cust_company_info
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_auth_application.ref_cust_company_info
```
