---
type: table
title: 协议迁移记录
page_key: argeement_migratory_record
belong: tables
status: draft
anchors: [argeement_migratory_record]
sources: ['database_schema:lowcode_pplatform.argeement_migratory_record']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, argeement_migratory_record__platform_product_code, argeement_migratory_record__status,
  argeement_migratory_record__agreement_type, argeement_migratory_record__sign_mode,
  argeement_migratory_record__is_new, argeement_migratory_record__enable]
---

# 协议迁移记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### identity

`name`, `cust_id`, `platform_product_code`, `organization_id`

### agreement

`agreement_type`, `agreement_path`, `agreement_name`, `agreement_no`, `effect_date`, `expire_date`

### sign

`sign_mode`, `sign_date`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### migrate

`status`, `is_new`, `pull_num`

## 字段

```ground:table
table: argeement_migratory_record
database: lowcode_pplatform
description: 协议迁移记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, agreement_name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 业务主体标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: agreement
  title: 协议信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: sign
  title: 签署信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.argeement_migratory_record
- key: migrate
  title: 迁移拉取状态
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: identity
- name: cust_id
  data_type: number
  description: 产融客户id
  cluster: identity
- name: platform_product_code
  data_type: string
  description: 产品编码
  cluster: identity
  dictionary: argeement_migratory_record__platform_product_code
- name: status
  data_type: number
  description: 状态
  cluster: migrate
  dictionary: argeement_migratory_record__status
- name: agreement_type
  data_type: string
  description: 协议类型
  cluster: agreement
  dictionary: argeement_migratory_record__agreement_type
- name: agreement_path
  data_type: string
  description: 协议路径
  cluster: agreement
- name: agreement_name
  data_type: string
  description: 协议名称
  cluster: agreement
- name: agreement_no
  data_type: string
  description: 协议编号
  cluster: agreement
- name: effect_date
  data_type: temporal
  description: 协议生效日
  cluster: agreement
- name: sign_mode
  data_type: string
  description: 签署模式
  cluster: sign
  dictionary: argeement_migratory_record__sign_mode
- name: expire_date
  data_type: temporal
  description: 失效时间
  cluster: agreement
- name: is_new
  data_type: string
  description: 是否新数据
  cluster: migrate
  dictionary: argeement_migratory_record__is_new
- name: pull_num
  data_type: number
  description: 拉取次数
  cluster: migrate
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: argeement_migratory_record__enable
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: act_procinst
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: identity
- name: sign_date
  data_type: temporal
  description: 签署日期
  cluster: sign
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: argeement_migratory_record.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.argeement_migratory_record.platform_product_code;database_profile:lowcode_pplatform.argeement_migratory_record.platform_product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 产品编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 2
  miss: 2
  deepened: false
  query_ok: true
  authenticity: unknown
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/argeement_migratory_record__platform_product_code]]（`argeement_migratory_record.platform_product_code`）
- [[dicts/argeement_migratory_record__status]]（`argeement_migratory_record.status`）
- [[dicts/argeement_migratory_record__agreement_type]]（`argeement_migratory_record.agreement_type`）
- [[dicts/argeement_migratory_record__sign_mode]]（`argeement_migratory_record.sign_mode`）
- [[dicts/argeement_migratory_record__is_new]]（`argeement_migratory_record.is_new`）
- [[dicts/argeement_migratory_record__enable]]（`argeement_migratory_record.enable`）
