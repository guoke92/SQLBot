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
related: [cust_auth_application, platform_product, tenant_setting_config, tenant_interworking_product,
  tenant_interworking_project, tenant_product_menu, tenant_product_menu_res, tenant_project,
  tenant_project_approval_business_info, tenant_product__platform_product_id, tenant_product__product_cate,
  tenant_product__max_financing_amount, tenant_product__product_agreement, tenant_product__open_status,
  tenant_product__max_financing_amount_flag, tenant_product__platform_product_code,
  tenant_product__is_migratory, tenant_product__view_order, tenant_product__ref_tenant_product_project_code,
  tenant_product__enable, tenant_product__multiple]
---

# 租户产品配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### status_flag

`open_status`, `max_financing_amount_flag`, `is_migratory`, `multiple`

### product_profile

`product_cate`, `product_summary`, `product_description`, `customer_group`, `credit_measures`, `transaction_structure`, `product_agreement`, `product_web_url`, `logo_icon_url`, `view_order`

### financing_limit

`max_financing_period`, `max_financing_amount`

### platform_ref

`platform_product_id`, `platform_product_code`

### tenant_ref

`tenant_id`, `ref_tenant_product_tenant_setting_config`, `ref_tenant_product_project_code`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: tenant_product
database: lowcode_pplatform
description: 租户产品配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: status_flag
  title: 状态标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: product_profile
  title: 产品资料
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: financing_limit
  title: 融资额度条款
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: platform_ref
  title: 平台产品关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: tenant_ref
  title: 租户关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product
- key: approval_flow
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
  cluster: platform_ref
  dictionary: tenant_product__platform_product_id
- name: product_cate
  data_type: string
  description: 产品类型
  cluster: product_profile
  dictionary: tenant_product__product_cate
- name: product_summary
  data_type: string
  description: 产品概述
  cluster: product_profile
- name: product_description
  data_type: string
  description: 产品详细描述
  cluster: product_profile
- name: customer_group
  data_type: string
  description: 客户群体
  cluster: product_profile
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  cluster: financing_limit
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  cluster: financing_limit
  dictionary: tenant_product__max_financing_amount
- name: credit_measures
  data_type: string
  description: 增信措施
  cluster: product_profile
- name: transaction_structure
  data_type: string
  description: 交易结构
  cluster: product_profile
- name: product_agreement
  data_type: string
  description: 产品协议
  cluster: product_profile
  dictionary: tenant_product__product_agreement
- name: tenant_id
  data_type: number
  description: 租户id
  cluster: tenant_ref
- name: open_status
  data_type: string
  description: 产品开通状态
  cluster: status_flag
  dictionary: tenant_product__open_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上线
  cluster: status_flag
  dictionary: tenant_product__max_financing_amount_flag
- name: platform_product_code
  data_type: string
  description: 平台产品编号
  cluster: platform_ref
  dictionary: tenant_product__platform_product_code
- name: product_web_url
  data_type: string
  description: 站点url
  cluster: product_profile
- name: is_migratory
  data_type: string
  description: 是否迁移标识,N代表未迁移,Y代表迁移
  cluster: status_flag
  dictionary: tenant_product__is_migratory
- name: logo_icon_url
  data_type: string
  description: 产品logo
  cluster: product_profile
- name: view_order
  data_type: number
  description: 展示顺序
  cluster: product_profile
  dictionary: tenant_product__view_order
- name: ref_tenant_product_tenant_setting_config
  data_type: string
  description: 租户-产品
  cluster: tenant_ref
- name: ref_tenant_product_project_code
  data_type: string
  description: 租户产品-平台产品
  cluster: tenant_ref
  dictionary: tenant_product__ref_tenant_product_project_code
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_ref
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_ref
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: tenant_ref
- name: multiple
  data_type: string
  description: 是否多个
  cluster: status_flag
  dictionary: tenant_product__multiple
```

## 关联关系

### likely — 值域支持较强

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
```

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.platform_product_code
right: tenant_product.ref_tenant_product_project_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_product.ref_tenant_product_project_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: ref_tenant_product_project_code
  comment: 码对码（平台产品编号）语义与本列注释'租户产品-平台产品'最接近，属可接受的 EQUI_JOIN 方向；但当前探测 overlap=0/8，需人工复核，若同表已
overlap:
  probed: true
  ratio: 0.0
  sample_size: 8
  authenticity: unlikely
authenticity_note: 码对码（平台产品编号）语义与本列注释'租户产品-平台产品'最接近，属可接受的 EQUI_JOIN 方向；但当前探测 overlap=0/8，需人工复核，若同表已有指向同一父表的
  id 主键边则本边标 secondary
```

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_project.platform_product_code
right: tenant_product.ref_tenant_product_project_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_product.ref_tenant_product_project_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: ref_tenant_product_project_code
  comment: 码对码（平台产品编号）方向与本列'租户产品-平台产品'语义相符，可接受为待确认的 EQUI_JOIN；overlap=0/8 需复核，若已有同父表
    id 主键边
overlap:
  probed: true
  ratio: 0.0
  sample_size: 8
  authenticity: unlikely
authenticity_note: 码对码（平台产品编号）方向与本列'租户产品-平台产品'语义相符，可接受为待确认的 EQUI_JOIN；overlap=0/8
  需复核，若已有同父表 id 主键边则标 secondary
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
```

## 页面链接

### 关联表

- [[tables/cust_auth_application]]
- [[tables/platform_product]]
- [[tables/tenant_setting_config]]
- [[tables/tenant_interworking_product]]
- [[tables/tenant_interworking_project]]
- [[tables/tenant_product_menu]]
- [[tables/tenant_product_menu_res]]
- [[tables/tenant_project]]
- [[tables/tenant_project_approval_business_info]]

### 字典

- [[dicts/tenant_product__platform_product_id]]（`tenant_product.platform_product_id`）
- [[dicts/tenant_product__product_cate]]（`tenant_product.product_cate`）
- [[dicts/tenant_product__max_financing_amount]]（`tenant_product.max_financing_amount`）
- [[dicts/tenant_product__product_agreement]]（`tenant_product.product_agreement`）
- [[dicts/tenant_product__open_status]]（`tenant_product.open_status`）
- [[dicts/tenant_product__max_financing_amount_flag]]（`tenant_product.max_financing_amount_flag`）
- [[dicts/tenant_product__platform_product_code]]（`tenant_product.platform_product_code`）
- [[dicts/tenant_product__is_migratory]]（`tenant_product.is_migratory`）
- [[dicts/tenant_product__view_order]]（`tenant_product.view_order`）
- [[dicts/tenant_product__ref_tenant_product_project_code]]（`tenant_product.ref_tenant_product_project_code`）
- [[dicts/tenant_product__enable]]（`tenant_product.enable`）
- [[dicts/tenant_product__multiple]]（`tenant_product.multiple`）
