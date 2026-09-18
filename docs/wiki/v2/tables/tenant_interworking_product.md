---
type: table
title: 租户互通产品
page_key: tenant_interworking_product
belong: tables
status: draft
anchors: [tenant_interworking_product]
sources: ['database_schema:lowcode_pplatform.tenant_interworking_product']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_interworking_product, platform_product, tenant_setting_config, tenant_interworking_project,
  tenant_interworking_product__product_cate, tenant_interworking_product__open_status,
  tenant_interworking_product__max_financing_amount_flag, tenant_interworking_product__platform_product_code,
  tenant_interworking_product__target_sys_channel, tenant_interworking_product__scope,
  tenant_interworking_product__ref_tenant_interworking_product_tenant_setting_config,
  tenant_interworking_product__enable]
---

# 租户互通产品

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product

`name`, `product_cate`, `open_status`, `logo_icon_url`, `credit_measures`, `transaction_structure`, `product_summary`, `product_description`, `customer_group`, `target_sys_channel`

### platform

`platform_product_id`, `platform_product_code`

### max_financing

`max_financing_amount_flag`, `max_financing_period`, `max_financing_amount`

### scope

`scope`, `scope_project`, `scope_role`

### ref_tenant

`ref_tenant_interworking_product_platform_product`, `ref_tenant_interworking_product_tenant_setting_config`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`tenant_id`, `app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: tenant_interworking_product
database: lowcode_pplatform
description: 租户互通产品
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: product
  title: 产品信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: platform
  title: 平台产品
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: max_financing
  title: 融资限额
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: scope
  title: 适用范围
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: ref_tenant
  title: 关联引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: tenant
  title: 租户标识
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: product
- name: platform_product_id
  data_type: number
  description: 平台产品id
  cluster: platform
- name: product_cate
  data_type: string
  description: 产品类型
  cluster: product
  dictionary: tenant_interworking_product__product_cate
- name: tenant_id
  data_type: number
  description: 租户id
  cluster: tenant
- name: open_status
  data_type: string
  description: 产品开通状态
  cluster: product
  dictionary: tenant_interworking_product__open_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上限
  cluster: max_financing
  dictionary: tenant_interworking_product__max_financing_amount_flag
- name: logo_icon_url
  data_type: string
  description: 产品logo
  cluster: product
- name: credit_measures
  data_type: string
  description: 增信措施
  cluster: product
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  cluster: max_financing
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  cluster: max_financing
- name: transaction_structure
  data_type: string
  description: 交易结构
  cluster: product
- name: platform_product_code
  data_type: string
  description: 平台产品编号
  cluster: platform
  dictionary: tenant_interworking_product__platform_product_code
- name: product_summary
  data_type: string
  description: 产品概述
  cluster: product
- name: product_description
  data_type: string
  description: 产品详细描述
  cluster: product
- name: customer_group
  data_type: string
  description: 客户群体
  cluster: product
- name: target_sys_channel
  data_type: string
  description: 目标系统ssochannel
  cluster: product
  dictionary: tenant_interworking_product__target_sys_channel
- name: scope
  data_type: string
  description: 适应范围标识
  cluster: scope
  dictionary: tenant_interworking_product__scope
- name: scope_project
  data_type: string
  description: 适用范围项目
  cluster: scope
- name: ref_tenant_interworking_product_platform_product
  data_type: string
  description: 关联产品大类
  cluster: ref_tenant
- name: ref_tenant_interworking_product_tenant_setting_config
  data_type: string
  description: 关联租户
  cluster: ref_tenant
  dictionary: tenant_interworking_product__ref_tenant_interworking_product_tenant_setting_config
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_interworking_product__enable
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
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
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
  cluster: tenant
- name: scope_role
  data_type: string
  description: 适用角色
  cluster: scope
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_interworking_product.platform_product_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.tenant_interworking_product.platform_product_id;database_profile:lowcode_pplatform.tenant_interworking_product.platform_product_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 11
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 值域完全覆盖(1.0)，列名/注释均为平台产品id，证据充分
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_interworking_product.ref_tenant_interworking_product_platform_product
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_interworking_product.ref_tenant_interworking_product_platform_product;database_profile:lowcode_pplatform.tenant_interworking_product.ref_tenant_interworking_product_platform_product
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: platform_product
  comment: 关联产品大类
overlap:
  probed: true
  ratio: 0.0
  sample_size: 3
  miss: 3
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 长ref命名指向platform_product，但重叠0/3，值域不契合
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config;database_profile:lowcode_pplatform.tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_setting_config
  comment: 关联租户
overlap:
  probed: true
  ratio: 0.0
  sample_size: 13
  miss: 13
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 长ref命名指向tenant_setting_config，但重叠0/13，值域不契合
```

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_interworking_product.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_interworking_product.platform_product_code;database_profile:lowcode_pplatform.tenant_interworking_product.platform_product_code
source: name
join_role: business_code
priority: secondary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品编号
overlap:
  probed: true
  ratio: 0.0
  sample_size: 11
  miss: 11
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名/注释有关联，但重叠率0/11，值域不契合；码对码候选需人工确认
```

## 页面链接

### 关联表

- [[tables/cust_interworking_product]]
- [[tables/platform_product]]
- [[tables/tenant_setting_config]]
- [[tables/tenant_interworking_project]]

### 字典

- [[dicts/tenant_interworking_product__product_cate]]（`tenant_interworking_product.product_cate`）
- [[dicts/tenant_interworking_product__open_status]]（`tenant_interworking_product.open_status`）
- [[dicts/tenant_interworking_product__max_financing_amount_flag]]（`tenant_interworking_product.max_financing_amount_flag`）
- [[dicts/tenant_interworking_product__platform_product_code]]（`tenant_interworking_product.platform_product_code`）
- [[dicts/tenant_interworking_product__target_sys_channel]]（`tenant_interworking_product.target_sys_channel`）
- [[dicts/tenant_interworking_product__scope]]（`tenant_interworking_product.scope`）
- [[dicts/tenant_interworking_product__ref_tenant_interworking_product_tenant_setting_config]]（`tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config`）
- [[dicts/tenant_interworking_product__enable]]（`tenant_interworking_product.enable`）
