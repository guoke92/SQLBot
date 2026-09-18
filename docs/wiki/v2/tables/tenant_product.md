---
type: table
title: 租户产品配置
page_key: tenant_product
belong: tables
status: draft
anchors: [tenant_product]
sources: ['database_schema:lowcode_pplatform.tenant_product']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_auth_application, platform_product, tenant_setting_config, tenant_product_menu,
  tenant_product_menu_res, tenant_project, tenant_project_approval_business_info,
  tenant_product__product_cate, tenant_product__open_status, tenant_product__max_financing_amount_flag,
  tenant_product__platform_product_code, tenant_product__is_migratory, tenant_product__enable,
  tenant_product__multiple]
---

# 租户产品配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### platform_product

`platform_product_id`, `product_cate`, `platform_product_code`

### product_content

`product_summary`, `product_description`, `product_agreement`, `product_web_url`, `logo_icon_url`, `view_order`

### product_terms

`customer_group`, `max_financing_period`, `max_financing_amount`, `credit_measures`, `transaction_structure`, `max_financing_amount_flag`

### tenant_scope

`tenant_id`, `ref_tenant_product_tenant_setting_config`, `ref_tenant_product_project_code`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### status_flag

`open_status`, `is_migratory`, `multiple`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: tenant_product
database: lowcode_pplatform
description: 租户产品配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, ref_tenant_product_project_code]
clusters:
- key: common
  title: 通用
  include: always
- key: platform_product
  title: 平台产品归属
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: product_content
  title: 产品内容与展示
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: product_terms
  title: 产品业务要素
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: tenant_scope
  title: 租户与机构归属
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: status_flag
  title: 状态与标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: approval
  title: 审批流程
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: platform_product_id
  data_type: number
  description: 平台产品id
  cluster: platform_product
- name: product_cate
  data_type: string
  description: 产品类型
  cluster: platform_product
  dictionary: tenant_product__product_cate
- name: product_summary
  data_type: string
  description: 产品概述
  cluster: product_content
- name: product_description
  data_type: string
  description: 产品详细描述
  cluster: product_content
- name: customer_group
  data_type: string
  description: 客户群体
  cluster: product_terms
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  cluster: product_terms
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  cluster: product_terms
- name: credit_measures
  data_type: string
  description: 增信措施
  cluster: product_terms
- name: transaction_structure
  data_type: string
  description: 交易结构
  cluster: product_terms
- name: product_agreement
  data_type: string
  description: 产品协议
  cluster: product_content
- name: tenant_id
  data_type: number
  description: 租户id
  cluster: tenant_scope
- name: open_status
  data_type: string
  description: 产品开通状态
  cluster: status_flag
  dictionary: tenant_product__open_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上线
  cluster: product_terms
  dictionary: tenant_product__max_financing_amount_flag
- name: platform_product_code
  data_type: string
  description: 平台产品编号
  cluster: platform_product
  dictionary: tenant_product__platform_product_code
- name: product_web_url
  data_type: string
  description: 站点url
  cluster: product_content
- name: is_migratory
  data_type: string
  description: 是否迁移标识,N代表未迁移,Y代表迁移
  cluster: status_flag
  dictionary: tenant_product__is_migratory
- name: logo_icon_url
  data_type: string
  description: 产品logo
  cluster: product_content
- name: view_order
  data_type: number
  description: 展示顺序
  cluster: product_content
- name: ref_tenant_product_tenant_setting_config
  data_type: string
  description: 租户-产品
  cluster: tenant_scope
- name: ref_tenant_product_project_code
  data_type: string
  description: 租户产品-平台产品
  cluster: tenant_scope
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_product__enable
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
  cluster: tenant_scope
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_scope
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
  cluster: tenant_scope
- name: multiple
  data_type: string
  description: 是否多个
  cluster: status_flag
  dictionary: tenant_product__multiple
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_product.platform_product_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.tenant_product.platform_product_id;database_profile:lowcode_pplatform.tenant_product.platform_product_id
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
  sample_size: 8
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 列名 exact_table 匹配且注释为平台产品id，探测 overlap=1.0（8/8 命中），值域契合，判 likely。
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_product.ref_tenant_product_tenant_setting_config
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_product.ref_tenant_product_tenant_setting_config;database_profile:lowcode_pplatform.tenant_product.ref_tenant_product_tenant_setting_config
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_setting_config
  comment: 租户-产品
overlap:
  probed: true
  ratio: 0.0061
  sample_size: 165
  miss: 164
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 长引用名指向 tenant_setting_config.id，但 overlap=0.0061（165 样本仅 1 命中），值域不契合，判
  unlikely。
```

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_product.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_product.platform_product_code;database_profile:lowcode_pplatform.tenant_product.platform_product_code
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
  sample_size: 8
  miss: 8
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名与注释有关联语义，但探测 overlap=0.0（8 样本全部未命中），值域不契合，判 unlikely，保留待人工复核。
```

## 页面链接

### 关联表

- [[tables/cust_auth_application]]
- [[tables/platform_product]]
- [[tables/tenant_setting_config]]
- [[tables/tenant_product_menu]]
- [[tables/tenant_product_menu_res]]
- [[tables/tenant_project]]
- [[tables/tenant_project_approval_business_info]]

### 字典

- [[dicts/tenant_product__product_cate]]（`tenant_product.product_cate`）
- [[dicts/tenant_product__open_status]]（`tenant_product.open_status`）
- [[dicts/tenant_product__max_financing_amount_flag]]（`tenant_product.max_financing_amount_flag`）
- [[dicts/tenant_product__platform_product_code]]（`tenant_product.platform_product_code`）
- [[dicts/tenant_product__is_migratory]]（`tenant_product.is_migratory`）
- [[dicts/tenant_product__enable]]（`tenant_product.enable`）
- [[dicts/tenant_product__multiple]]（`tenant_product.multiple`）
