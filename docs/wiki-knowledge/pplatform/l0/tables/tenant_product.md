---
type: table
title: 租户产品配置
page_key: tenant_product
belong: tables
status: draft
aliases: []
anchors:
- tenant_product
sources:
- database_schema:lowcode_pplatform.tenant_product
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户产品配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_profile

`name`, `product_cate`, `product_summary`, `product_description`, `customer_group`, `product_agreement`, `product_web_url`, `logo_icon_url`, `view_order`

### financing_terms

`max_financing_period`, `max_financing_amount`, `credit_measures`, `transaction_structure`, `max_financing_amount_flag`

### platform_link

`platform_product_id`, `platform_product_code`, `ref_tenant_product_project_code`

### tenant_scope

`tenant_id`, `ref_tenant_product_tenant_setting_config`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### status_flag

`open_status`, `is_migratory`, `multiple`

### 未归簇

`remark`

## 字段

```ground:table
table: tenant_product
database: lowcode_pplatform
description: 租户产品配置
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- platform_product_code
- ref_tenant_product_project_code
clusters:
- key: common
  title: 通用
  include: always
- key: product_profile
  title: 产品主档信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: financing_terms
  title: 融资要素
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: platform_link
  title: 平台产品关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: tenant_scope
  title: 租户与机构归属
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: approval_flow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: status_flag
  title: 状态与标记
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
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
  cluster: product_profile
- name: platform_product_id
  data_type: number
  description: 平台产品id
  nullable: true
  cluster: platform_link
- name: product_cate
  data_type: string
  description: 产品类型
  nullable: true
  cluster: product_profile
  dictionary: tenant_product_product_cate
- name: product_summary
  data_type: string
  description: 产品概述
  nullable: true
  cluster: product_profile
- name: product_description
  data_type: string
  description: 产品详细描述
  nullable: true
  cluster: product_profile
- name: customer_group
  data_type: string
  description: 客户群体
  nullable: true
  cluster: product_profile
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  nullable: true
  cluster: financing_terms
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  nullable: true
  cluster: financing_terms
- name: credit_measures
  data_type: string
  description: 增信措施
  nullable: true
  cluster: financing_terms
- name: transaction_structure
  data_type: string
  description: 交易结构
  nullable: true
  cluster: financing_terms
- name: product_agreement
  data_type: string
  description: 产品协议
  nullable: true
  cluster: product_profile
- name: tenant_id
  data_type: number
  description: 租户id
  nullable: true
  cluster: tenant_scope
- name: open_status
  data_type: string
  description: 产品开通状态
  nullable: true
  cluster: status_flag
  dictionary: tenant_product_open_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上线
  nullable: true
  cluster: financing_terms
  dictionary: tenant_product_max_financing_amount_flag
- name: platform_product_code
  data_type: string
  description: 平台产品编号
  nullable: true
  cluster: platform_link
  dictionary: tenant_product_platform_product_code
- name: product_web_url
  data_type: string
  description: 站点url
  nullable: true
  cluster: product_profile
- name: is_migratory
  data_type: string
  description: 是否迁移标识,N代表未迁移,Y代表迁移
  nullable: true
  cluster: status_flag
  dictionary: tenant_product_is_migratory
- name: logo_icon_url
  data_type: string
  description: 产品logo
  nullable: true
  cluster: product_profile
- name: view_order
  data_type: number
  description: 展示顺序
  nullable: true
  cluster: product_profile
- name: ref_tenant_product_tenant_setting_config
  data_type: string
  description: 租户-产品
  nullable: true
  cluster: tenant_scope
- name: ref_tenant_product_project_code
  data_type: string
  description: 租户产品-平台产品
  nullable: true
  cluster: platform_link
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_product_enable
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
  cluster: tenant_scope
- name: multiple
  data_type: string
  description: 是否多个
  nullable: true
  cluster: status_flag
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_product.platform_product_id
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.tenant_product.platform_product_id
```

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_product.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.tenant_product.platform_product_code
```
