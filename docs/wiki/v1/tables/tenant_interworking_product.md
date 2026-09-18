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
  tenant_product, tenant_interworking_product__platform_product_id, tenant_interworking_product__product_cate,
  tenant_interworking_product__open_status, tenant_interworking_product__max_financing_amount_flag,
  tenant_interworking_product__credit_measures, tenant_interworking_product__max_financing_period,
  tenant_interworking_product__max_financing_amount, tenant_interworking_product__platform_product_code,
  tenant_interworking_product__target_sys_channel, tenant_interworking_product__scope,
  tenant_interworking_product__ref_tenant_interworking_product_platform_product, tenant_interworking_product__ref_tenant_interworking_product_tenant_setting_config,
  tenant_interworking_product__enable, tenant_interworking_product__app_tenant_code,
  tenant_interworking_product__db_tenant_code, tenant_interworking_product__scope_role]
---

# 租户互通产品

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_info

`name`, `product_cate`, `open_status`, `logo_icon_url`, `credit_measures`, `transaction_structure`, `product_summary`, `product_description`, `customer_group`

### platform_access

`platform_product_id`, `platform_product_code`, `target_sys_channel`

### financing_limit

`max_financing_amount_flag`, `max_financing_period`, `max_financing_amount`

### scope_apply

`scope`, `scope_project`, `scope_role`

### ref_link

`ref_tenant_interworking_product_platform_product`, `ref_tenant_interworking_product_tenant_setting_config`

### tenant_org

`tenant_id`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

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
- key: product_info
  title: 产品信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: platform_access
  title: 平台对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: financing_limit
  title: 融资要素
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: scope_apply
  title: 适用范围
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: ref_link
  title: 关联引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_product
- key: approval
  title: 审批流程
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
  cluster: product_info
- name: platform_product_id
  data_type: number
  description: 平台产品id
  cluster: platform_access
  dictionary: tenant_interworking_product__platform_product_id
- name: product_cate
  data_type: string
  description: 产品类型
  cluster: product_info
  dictionary: tenant_interworking_product__product_cate
- name: tenant_id
  data_type: number
  description: 租户id
  cluster: tenant_org
- name: open_status
  data_type: string
  description: 产品开通状态
  cluster: product_info
  dictionary: tenant_interworking_product__open_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上限
  cluster: financing_limit
  dictionary: tenant_interworking_product__max_financing_amount_flag
- name: logo_icon_url
  data_type: string
  description: 产品logo
  cluster: product_info
- name: credit_measures
  data_type: string
  description: 增信措施
  cluster: product_info
  dictionary: tenant_interworking_product__credit_measures
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  cluster: financing_limit
  dictionary: tenant_interworking_product__max_financing_period
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  cluster: financing_limit
  dictionary: tenant_interworking_product__max_financing_amount
- name: transaction_structure
  data_type: string
  description: 交易结构
  cluster: product_info
- name: platform_product_code
  data_type: string
  description: 平台产品编号
  cluster: platform_access
  dictionary: tenant_interworking_product__platform_product_code
- name: product_summary
  data_type: string
  description: 产品概述
  cluster: product_info
- name: product_description
  data_type: string
  description: 产品详细描述
  cluster: product_info
- name: customer_group
  data_type: string
  description: 客户群体
  cluster: product_info
- name: target_sys_channel
  data_type: string
  description: 目标系统ssochannel
  cluster: platform_access
  dictionary: tenant_interworking_product__target_sys_channel
- name: scope
  data_type: string
  description: 适应范围标识
  cluster: scope_apply
  dictionary: tenant_interworking_product__scope
- name: scope_project
  data_type: string
  description: 适用范围项目
  cluster: scope_apply
- name: ref_tenant_interworking_product_platform_product
  data_type: string
  description: 关联产品大类
  cluster: ref_link
  dictionary: tenant_interworking_product__ref_tenant_interworking_product_platform_product
- name: ref_tenant_interworking_product_tenant_setting_config
  data_type: string
  description: 关联租户
  cluster: ref_link
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_org
  dictionary: tenant_interworking_product__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
  dictionary: tenant_interworking_product__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: tenant_org
- name: scope_role
  data_type: string
  description: 适用角色
  cluster: scope_apply
  dictionary: tenant_interworking_product__scope_role
```

## 关联关系

### likely — 值域支持较强

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
authenticity_note: 左 platform_product.id；名称证据 exact_table 且注释「平台产品id」直指主键，探测 11/11
  命中、0 miss，判为可靠主键边。
```

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_interworking_product.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
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
authenticity_note: 左 platform_product.code；名称证据 exact_table 支持（平台产品编号），但探测 11/11 全部未命中，两侧编码体系可能不同或父表
  code 非业务编号，名称与探测结论冲突，保留人工复核。
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
authenticity_note: 左 platform_product.id；长引用名虽指向 platform_product，但本列值为 UUID 与数值型平台产品主键值域不符，探测
  3/3 全 miss，可能指向其他「产品大类」实体。
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
authenticity_note: 左 tenant_setting_config.id；长引用名指向租户配置表，但本列为 UUID 且探测 13/13 全 miss，判为不可靠边。
```

## 页面链接

### 关联表

- [[tables/cust_interworking_product]]
- [[tables/platform_product]]
- [[tables/tenant_setting_config]]
- [[tables/tenant_interworking_project]]
- [[tables/tenant_product]]

### 字典

- [[dicts/tenant_interworking_product__platform_product_id]]（`tenant_interworking_product.platform_product_id`）
- [[dicts/tenant_interworking_product__product_cate]]（`tenant_interworking_product.product_cate`）
- [[dicts/tenant_interworking_product__open_status]]（`tenant_interworking_product.open_status`）
- [[dicts/tenant_interworking_product__max_financing_amount_flag]]（`tenant_interworking_product.max_financing_amount_flag`）
- [[dicts/tenant_interworking_product__credit_measures]]（`tenant_interworking_product.credit_measures`）
- [[dicts/tenant_interworking_product__max_financing_period]]（`tenant_interworking_product.max_financing_period`）
- [[dicts/tenant_interworking_product__max_financing_amount]]（`tenant_interworking_product.max_financing_amount`）
- [[dicts/tenant_interworking_product__platform_product_code]]（`tenant_interworking_product.platform_product_code`）
- [[dicts/tenant_interworking_product__target_sys_channel]]（`tenant_interworking_product.target_sys_channel`）
- [[dicts/tenant_interworking_product__scope]]（`tenant_interworking_product.scope`）
- [[dicts/tenant_interworking_product__ref_tenant_interworking_product_platform_product]]（`tenant_interworking_product.ref_tenant_interworking_product_platform_product`）
- [[dicts/tenant_interworking_product__ref_tenant_interworking_product_tenant_setting_config]]（`tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config`）
- [[dicts/tenant_interworking_product__enable]]（`tenant_interworking_product.enable`）
- [[dicts/tenant_interworking_product__app_tenant_code]]（`tenant_interworking_product.app_tenant_code`）
- [[dicts/tenant_interworking_product__db_tenant_code]]（`tenant_interworking_product.db_tenant_code`）
- [[dicts/tenant_interworking_product__scope_role]]（`tenant_interworking_product.scope_role`）
