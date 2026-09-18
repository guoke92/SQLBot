---
type: table
title: 平台产品基础配置
page_key: platform_product
belong: tables
status: draft
anchors: [platform_product]
sources: ['database_schema:lowcode_pplatform.platform_product']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [argeement_migratory_record, authorization_agreement, cust_auth_application,
  cust_interworking_product, cust_project_rel, platform_product_cust_role, platform_product_client,
  tenant_interworking_product, tenant_interworking_project, tenant_migarory_log, tenant_migarory_log_bak,
  tenant_product, tenant_project, platform_product__product_type, platform_product__platform_flag,
  platform_product__platform_code, platform_product__multiple_project_flag, platform_product__multiple_cust_role_flag,
  platform_product__product_code, platform_product__product_cate, platform_product__product_status,
  platform_product__product_construction_status, platform_product__max_financing_amount_flag,
  platform_product__multiple_client_type, platform_product__menu_type, platform_product__wkfl_flag,
  platform_product__enable, platform_product__act_procinst_status, platform_product__general_flag]
---

# 平台产品基础配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`, `product_type`, `product_code`, `product_cate`, `basic_product`, `general_flag`

### product_profile

`product_summary`, `product_description`, `product_ref_num`, `product_status`, `product_construction_status`, `logo_icon_url`

### platform

`platform_flag`, `platform_code`

### multi

`multiple_project_flag`, `multiple_cust_role_flag`, `multiple_client_type`, `cust_role_combine`

### financing

`customer_group`, `max_financing_period`, `max_financing_amount`, `credit_measures`, `transaction_structure`, `max_financing_amount_flag`

### project_config

`project_code`, `app_code`, `menu_type`, `default_menu_code`, `default_menu_index`, `wkfl_flag`, `project_config`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### scope

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: platform_product
database: lowcode_pplatform
description: 平台产品基础配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, platform_code, project_code, app_code, default_menu_code]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 产品标识与分类
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: product_profile
  title: 产品资料
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: platform
  title: 平台属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: multi
  title: 多项目与多角色
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: financing
  title: 融资要素
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: project_config
  title: 项目与前端配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: scope
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
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
- name: product_type
  data_type: string
  description: 通用产品标识
  cluster: identity
  dictionary: platform_product__product_type
- name: platform_flag
  data_type: string
  description: 是否平台标识
  cluster: platform
  dictionary: platform_product__platform_flag
- name: platform_code
  data_type: string
  description: 平台编码
  cluster: platform
  dictionary: platform_product__platform_code
- name: multiple_project_flag
  data_type: string
  description: 是否有多项目
  cluster: multi
  dictionary: platform_product__multiple_project_flag
- name: multiple_cust_role_flag
  data_type: string
  description: 是否有多企业角色
  cluster: multi
  dictionary: platform_product__multiple_cust_role_flag
- name: product_code
  data_type: string
  description: 产品编码
  cluster: identity
  dictionary: platform_product__product_code
- name: product_cate
  data_type: string
  description: 产品类型
  cluster: identity
  dictionary: platform_product__product_cate
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
  cluster: financing
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  cluster: financing
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  cluster: financing
- name: credit_measures
  data_type: string
  description: 增信措施
  cluster: financing
- name: transaction_structure
  data_type: string
  description: 交易结构
  cluster: financing
- name: product_ref_num
  data_type: number
  description: 引用产品的平台数
  cluster: product_profile
- name: product_status
  data_type: string
  description: 产品状态
  cluster: product_profile
  dictionary: platform_product__product_status
- name: product_construction_status
  data_type: string
  description: 产品建设情况
  cluster: product_profile
  dictionary: platform_product__product_construction_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上线
  cluster: financing
  dictionary: platform_product__max_financing_amount_flag
- name: multiple_client_type
  data_type: string
  description: 多端口类型
  cluster: multi
  dictionary: platform_product__multiple_client_type
- name: project_code
  data_type: string
  description: 蜂搭平台项目编号
  cluster: project_config
- name: app_code
  data_type: string
  description: 蜂搭平台app编号
  cluster: project_config
- name: basic_product
  data_type: string
  description: 是否是产融底座
  cluster: identity
- name: menu_type
  data_type: string
  description: 菜单展示类型(topLeft/left)
  cluster: project_config
  dictionary: platform_product__menu_type
- name: default_menu_code
  data_type: string
  description: 默认菜单编号
  cluster: project_config
- name: default_menu_index
  data_type: number
  description: 默认菜单编号
  cluster: project_config
- name: wkfl_flag
  data_type: string
  description: 产品工作流启用开关
  cluster: project_config
  dictionary: platform_product__wkfl_flag
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: platform_product__enable
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
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: scope
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: scope
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
  dictionary: platform_product__act_procinst_status
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: scope
- name: logo_icon_url
  data_type: string
  description: 产品logo
  cluster: product_profile
- name: cust_role_combine
  data_type: string
  description: 支持企业角色组合
  cluster: multi
- name: general_flag
  data_type: string
  description: 通用产品标识
  cluster: identity
  dictionary: platform_product__general_flag
- name: project_config
  data_type: string
  description: 项目配置
  cluster: project_config
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: platform_product_cust_role.product_code
right: platform_product.product_ref_num
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.platform_product.product_ref_num
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: product_ref_num
  comment: 引用产品的平台数
overlap:
  probed: true
  ratio: 1.0
  sample_size: 12
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: platform_product_cust_role.product_code
right: platform_product.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.platform_product.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 同名列码对码，overlap 0.5/反向 0.8333，可作 EQUI_JOIN 候选边。
overlap:
  probed: true
  ratio: 0.5
  ratio_reverse: 0.8333
  sample_size: 20
  authenticity: unknown
authenticity_note: 同名列码对码，overlap 0.5/反向 0.8333，可作 EQUI_JOIN 候选边。
```

## 页面链接

### 关联表

- [[tables/argeement_migratory_record]]
- [[tables/authorization_agreement]]
- [[tables/cust_auth_application]]
- [[tables/cust_interworking_product]]
- [[tables/cust_project_rel]]
- [[tables/platform_product_cust_role]]
- [[tables/platform_product_client]]
- [[tables/tenant_interworking_product]]
- [[tables/tenant_interworking_project]]
- [[tables/tenant_migarory_log]]
- [[tables/tenant_migarory_log_bak]]
- [[tables/tenant_product]]
- [[tables/tenant_project]]

### 字典

- [[dicts/platform_product__product_type]]（`platform_product.product_type`）
- [[dicts/platform_product__platform_flag]]（`platform_product.platform_flag`）
- [[dicts/platform_product__platform_code]]（`platform_product.platform_code`）
- [[dicts/platform_product__multiple_project_flag]]（`platform_product.multiple_project_flag`）
- [[dicts/platform_product__multiple_cust_role_flag]]（`platform_product.multiple_cust_role_flag`）
- [[dicts/platform_product__product_code]]（`platform_product.product_code`）
- [[dicts/platform_product__product_cate]]（`platform_product.product_cate`）
- [[dicts/platform_product__product_status]]（`platform_product.product_status`）
- [[dicts/platform_product__product_construction_status]]（`platform_product.product_construction_status`）
- [[dicts/platform_product__max_financing_amount_flag]]（`platform_product.max_financing_amount_flag`）
- [[dicts/platform_product__multiple_client_type]]（`platform_product.multiple_client_type`）
- [[dicts/platform_product__menu_type]]（`platform_product.menu_type`）
- [[dicts/platform_product__wkfl_flag]]（`platform_product.wkfl_flag`）
- [[dicts/platform_product__enable]]（`platform_product.enable`）
- [[dicts/platform_product__act_procinst_status]]（`platform_product.act_procinst_status`）
- [[dicts/platform_product__general_flag]]（`platform_product.general_flag`）
