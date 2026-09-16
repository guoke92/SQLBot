---
type: table
title: 协议迁移记录
page_key: argeement_migratory_record
belong: tables
status: draft
aliases: []
anchors:
- argeement_migratory_record
sources:
- database_schema:lowcode_pplatform.argeement_migratory_record
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 协议迁移记录

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### agreement

`agreement_type`, `agreement_path`, `agreement_name`, `agreement_no`, `effect_date`, `expire_date`

### sign

`sign_mode`, `sign_date`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### customer_org

`cust_id`, `organization_id`

### migration

`name`, `status`, `is_new`, `pull_num`, `remark`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`platform_product_code`

## 字段

```ground:table
table: argeement_migratory_record
database: lowcode_pplatform
description: 协议迁移记录
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- platform_product_code
- agreement_name
clusters:
- key: common
  title: 通用
  include: always
- key: agreement
  title: 协议信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: sign
  title: 签署信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: customer_org
  title: 客户与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: migration
  title: 迁移记录信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
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
  cluster: migration
- name: cust_id
  data_type: number
  description: 产融客户id
  nullable: true
  cluster: customer_org
- name: platform_product_code
  data_type: string
  description: 产品编码
  nullable: true
- name: status
  data_type: number
  description: 状态
  nullable: true
  cluster: migration
  dictionary: argeement_migratory_record_status
- name: agreement_type
  data_type: string
  description: 协议类型
  nullable: true
  cluster: agreement
  dictionary: argeement_migratory_record_agreement_type
- name: agreement_path
  data_type: string
  description: 协议路径
  nullable: true
  cluster: agreement
- name: agreement_name
  data_type: string
  description: 协议名称
  nullable: true
  cluster: agreement
- name: agreement_no
  data_type: string
  description: 协议编号
  nullable: true
  cluster: agreement
- name: effect_date
  data_type: temporal
  description: 协议生效日
  nullable: true
  cluster: agreement
- name: sign_mode
  data_type: string
  description: 签署模式
  nullable: true
  cluster: sign
- name: expire_date
  data_type: temporal
  description: 失效时间
  nullable: true
  cluster: agreement
- name: is_new
  data_type: string
  description: 是否新数据
  nullable: true
  cluster: migration
  dictionary: argeement_migratory_record_is_new
- name: pull_num
  data_type: number
  description: 拉取次数
  nullable: true
  cluster: migration
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: migration
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
  cluster: customer_org
- name: sign_date
  data_type: temporal
  description: 签署日期
  nullable: true
  cluster: sign
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: argeement_migratory_record.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.argeement_migratory_record.platform_product_code
```
