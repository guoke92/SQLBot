---
type: table
title: 企业互通产品
page_key: cust_interworking_product
belong: tables
status: draft
aliases: []
anchors:
- cust_interworking_product
sources:
- database_schema:lowcode_pplatform.cust_interworking_product
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 企业互通产品

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_info

`name`, `platform_product_code`, `product_id`, `ref_cust_interworking_product_tenant_interworking_product`

### open_info

`open_status`, `open_time`, `open_user`

### agree_info

`agree_authorization_flag`, `agree_authorization_time`

### customer_org

`cust_id`, `ref_cust_interworking_product_cust_company_info`, `organization_id`

### tenant

`tenant_id`, `app_tenant_code`, `db_tenant_code`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`remark`

## 字段

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
description: 企业互通产品
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
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: open_info
  title: 开通信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: agree_info
  title: 授权信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: customer_org
  title: 企业/机构关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
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
  cluster: product_info
- name: open_status
  data_type: string
  description: 开通状态
  nullable: true
  cluster: open_info
  dictionary: cust_interworking_product_open_status
- name: cust_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: customer_org
- name: open_time
  data_type: temporal
  description: 开通时间
  nullable: true
  cluster: open_info
- name: open_user
  data_type: number
  description: 开通人
  nullable: true
  cluster: open_info
- name: platform_product_code
  data_type: string
  description: 平台产品编码
  nullable: true
  cluster: product_info
- name: agree_authorization_flag
  data_type: string
  description: 是否同意授权
  nullable: true
  cluster: agree_info
  dictionary: cust_interworking_product_agree_authorization_flag
- name: agree_authorization_time
  data_type: temporal
  description: 同意授权时间
  nullable: true
  cluster: agree_info
- name: product_id
  data_type: number
  description: 互通产品id
  nullable: true
  cluster: product_info
- name: tenant_id
  data_type: number
  description: 租户id
  nullable: true
  cluster: tenant
- name: ref_cust_interworking_product_cust_company_info
  data_type: string
  description: 关联企业
  nullable: true
  cluster: customer_org
- name: ref_cust_interworking_product_tenant_interworking_product
  data_type: string
  description: 关联互通产品
  nullable: true
  cluster: product_info
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_interworking_product_enable
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
  cluster: customer_org
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: cust_interworking_product.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_interworking_product.platform_product_code
```
