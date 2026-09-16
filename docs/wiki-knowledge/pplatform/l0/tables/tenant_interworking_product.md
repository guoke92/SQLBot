---
type: table
title: 租户互通产品
page_key: tenant_interworking_product
belong: tables
status: draft
aliases: []
anchors:
- tenant_interworking_product
sources:
- database_schema:lowcode_pplatform.tenant_interworking_product
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户互通产品

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product

`name`, `product_cate`, `logo_icon_url`, `product_summary`, `product_description`

### platform_ref

`platform_product_id`, `platform_product_code`, `ref_tenant_interworking_product_platform_product`

### financing

`max_financing_amount_flag`, `credit_measures`, `max_financing_period`, `max_financing_amount`, `transaction_structure`, `customer_group`

### scope

`scope`, `scope_project`, `scope_role`

### tenant

`tenant_id`, `ref_tenant_interworking_product_tenant_setting_config`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### channel

`open_status`, `target_sys_channel`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: tenant_interworking_product
database: lowcode_pplatform
description: 租户互通产品
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
  title: 通用与审计
  include: always
- key: product
  title: 产品信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: platform_ref
  title: 平台产品关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: financing
  title: 融资条件
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: scope
  title: 适用范围
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: tenant
  title: 租户与机构标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: channel
  title: 渠道与开通
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
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
  cluster: product
- name: platform_product_id
  data_type: number
  description: 平台产品id
  nullable: true
  cluster: platform_ref
- name: product_cate
  data_type: string
  description: 产品类型
  nullable: true
  cluster: product
  dictionary: tenant_interworking_product_product_cate
- name: tenant_id
  data_type: number
  description: 租户id
  nullable: true
  cluster: tenant
- name: open_status
  data_type: string
  description: 产品开通状态
  nullable: true
  cluster: channel
  dictionary: tenant_interworking_product_open_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上限
  nullable: true
  cluster: financing
  dictionary: tenant_interworking_product_max_financing_amount_flag
- name: logo_icon_url
  data_type: string
  description: 产品logo
  nullable: true
  cluster: product
- name: credit_measures
  data_type: string
  description: 增信措施
  nullable: true
  cluster: financing
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  nullable: true
  cluster: financing
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  nullable: true
  cluster: financing
- name: transaction_structure
  data_type: string
  description: 交易结构
  nullable: true
  cluster: financing
- name: platform_product_code
  data_type: string
  description: 平台产品编号
  nullable: true
  cluster: platform_ref
- name: product_summary
  data_type: string
  description: 产品概述
  nullable: true
  cluster: product
- name: product_description
  data_type: string
  description: 产品详细描述
  nullable: true
  cluster: product
- name: customer_group
  data_type: string
  description: 客户群体
  nullable: true
  cluster: financing
- name: target_sys_channel
  data_type: string
  description: 目标系统ssochannel
  nullable: true
  cluster: channel
- name: scope
  data_type: string
  description: 适应范围标识
  nullable: true
  cluster: scope
  dictionary: tenant_interworking_product_scope
- name: scope_project
  data_type: string
  description: 适用范围项目
  nullable: true
  cluster: scope
- name: ref_tenant_interworking_product_platform_product
  data_type: string
  description: 关联产品大类
  nullable: true
  cluster: platform_ref
- name: ref_tenant_interworking_product_tenant_setting_config
  data_type: string
  description: 关联租户
  nullable: true
  cluster: tenant
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_interworking_product_enable
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
  cluster: tenant
- name: scope_role
  data_type: string
  description: 适用角色
  nullable: true
  cluster: scope
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_interworking_product.platform_product_id
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.tenant_interworking_product.platform_product_id
```

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_interworking_product.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.tenant_interworking_product.platform_product_code
```
