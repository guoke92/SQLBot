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
  tenant_product, tenant_project, platform_product__code, platform_product__product_type,
  platform_product__platform_flag, platform_product__platform_code, platform_product__multiple_project_flag,
  platform_product__multiple_cust_role_flag, platform_product__product_code, platform_product__product_cate,
  platform_product__product_ref_num, platform_product__product_status, platform_product__product_construction_status,
  platform_product__max_financing_amount_flag, platform_product__multiple_client_type,
  platform_product__project_code, platform_product__app_code, platform_product__menu_type,
  platform_product__default_menu_index, platform_product__wkfl_flag, platform_product__enable,
  platform_product__app_tenant_code, platform_product__db_tenant_code, platform_product__act_procinst_status,
  platform_product__general_flag]
---

# 平台产品基础配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_master

`product_type`, `product_code`, `product_cate`, `product_summary`, `product_description`, `product_ref_num`, `product_status`, `product_construction_status`, `basic_product`, `general_flag`

### platform_project_bind

`platform_flag`, `platform_code`, `project_code`, `app_code`, `project_config`

### org_tenant

`app_tenant_code`, `db_tenant_code`, `organization_id`

### financing_terms

`customer_group`, `max_financing_period`, `max_financing_amount`, `credit_measures`, `transaction_structure`, `max_financing_amount_flag`

### multi_role

`multiple_project_flag`, `multiple_cust_role_flag`, `multiple_client_type`, `cust_role_combine`

### menu_display

`menu_type`, `default_menu_code`, `default_menu_index`, `logo_icon_url`

### workflow

`wkfl_flag`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

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
- key: product_master
  title: 产品主数据
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: platform_project_bind
  title: 平台与项目绑定
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: org_tenant
  title: 机构与租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: financing_terms
  title: 融资要素与增信
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: multi_role
  title: 多项目与多角色
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: menu_display
  title: 菜单与展示配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product
- key: workflow
  title: 流程审批
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
  dictionary: platform_product__code
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: product_type
  data_type: string
  description: 通用产品标识
  cluster: product_master
  dictionary: platform_product__product_type
- name: platform_flag
  data_type: string
  description: 是否平台标识
  cluster: platform_project_bind
  dictionary: platform_product__platform_flag
- name: platform_code
  data_type: string
  description: 平台编码
  cluster: platform_project_bind
  dictionary: platform_product__platform_code
- name: multiple_project_flag
  data_type: string
  description: 是否有多项目
  cluster: multi_role
  dictionary: platform_product__multiple_project_flag
- name: multiple_cust_role_flag
  data_type: string
  description: 是否有多企业角色
  cluster: multi_role
  dictionary: platform_product__multiple_cust_role_flag
- name: product_code
  data_type: string
  description: 产品编码
  cluster: product_master
  dictionary: platform_product__product_code
- name: product_cate
  data_type: string
  description: 产品类型
  cluster: product_master
  dictionary: platform_product__product_cate
- name: product_summary
  data_type: string
  description: 产品概述
  cluster: product_master
- name: product_description
  data_type: string
  description: 产品详细描述
  cluster: product_master
- name: customer_group
  data_type: string
  description: 客户群体
  cluster: financing_terms
- name: max_financing_period
  data_type: string
  description: 融资期限上限
  cluster: financing_terms
- name: max_financing_amount
  data_type: string
  description: 融资金额上限
  cluster: financing_terms
- name: credit_measures
  data_type: string
  description: 增信措施
  cluster: financing_terms
- name: transaction_structure
  data_type: string
  description: 交易结构
  cluster: financing_terms
- name: product_ref_num
  data_type: number
  description: 引用产品的平台数
  cluster: product_master
  dictionary: platform_product__product_ref_num
- name: product_status
  data_type: string
  description: 产品状态
  cluster: product_master
  dictionary: platform_product__product_status
- name: product_construction_status
  data_type: string
  description: 产品建设情况
  cluster: product_master
  dictionary: platform_product__product_construction_status
- name: max_financing_amount_flag
  data_type: string
  description: 是否限额融资资金上线
  cluster: financing_terms
  dictionary: platform_product__max_financing_amount_flag
- name: multiple_client_type
  data_type: string
  description: 多端口类型
  cluster: multi_role
  dictionary: platform_product__multiple_client_type
- name: project_code
  data_type: string
  description: 蜂搭平台项目编号
  cluster: platform_project_bind
  dictionary: platform_product__project_code
- name: app_code
  data_type: string
  description: 蜂搭平台app编号
  cluster: platform_project_bind
  dictionary: platform_product__app_code
- name: basic_product
  data_type: string
  description: 是否是产融底座
  cluster: product_master
- name: menu_type
  data_type: string
  description: 菜单展示类型(topLeft/left)
  cluster: menu_display
  dictionary: platform_product__menu_type
- name: default_menu_code
  data_type: string
  description: 默认菜单编号
  cluster: menu_display
- name: default_menu_index
  data_type: number
  description: 默认菜单编号
  cluster: menu_display
  dictionary: platform_product__default_menu_index
- name: wkfl_flag
  data_type: string
  description: 产品工作流启用开关
  cluster: workflow
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
  cluster: org_tenant
  dictionary: platform_product__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: org_tenant
  dictionary: platform_product__db_tenant_code
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
  cluster: org_tenant
- name: logo_icon_url
  data_type: string
  description: 产品logo
  cluster: menu_display
- name: cust_role_combine
  data_type: string
  description: 支持企业角色组合
  cluster: multi_role
- name: general_flag
  data_type: string
  description: 通用产品标识
  cluster: product_master
  dictionary: platform_product__general_flag
- name: project_config
  data_type: string
  description: 项目配置
  cluster: platform_project_bind
```

## 关联关系

### likely — 值域支持较强

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
  comment: 码对码 EQUI_JOIN，列名与注释均为产品编码，重叠率 0.5、反向 0.8333，属合法代码关联；若同表另有指向本表 id 的主键边，此码边应记为
    sec
overlap:
  probed: true
  ratio: 0.5
  ratio_reverse: 0.8333
  sample_size: 20
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN，列名与注释均为产品编码，重叠率 0.5、反向 0.8333，属合法代码关联；若同表另有指向本表 id
  的主键边，此码边应记为 secondary。
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

- [[dicts/platform_product__code]]（`platform_product.code`）
- [[dicts/platform_product__product_type]]（`platform_product.product_type`）
- [[dicts/platform_product__platform_flag]]（`platform_product.platform_flag`）
- [[dicts/platform_product__platform_code]]（`platform_product.platform_code`）
- [[dicts/platform_product__multiple_project_flag]]（`platform_product.multiple_project_flag`）
- [[dicts/platform_product__multiple_cust_role_flag]]（`platform_product.multiple_cust_role_flag`）
- [[dicts/platform_product__product_code]]（`platform_product.product_code`）
- [[dicts/platform_product__product_cate]]（`platform_product.product_cate`）
- [[dicts/platform_product__product_ref_num]]（`platform_product.product_ref_num`）
- [[dicts/platform_product__product_status]]（`platform_product.product_status`）
- [[dicts/platform_product__product_construction_status]]（`platform_product.product_construction_status`）
- [[dicts/platform_product__max_financing_amount_flag]]（`platform_product.max_financing_amount_flag`）
- [[dicts/platform_product__multiple_client_type]]（`platform_product.multiple_client_type`）
- [[dicts/platform_product__project_code]]（`platform_product.project_code`）
- [[dicts/platform_product__app_code]]（`platform_product.app_code`）
- [[dicts/platform_product__menu_type]]（`platform_product.menu_type`）
- [[dicts/platform_product__default_menu_index]]（`platform_product.default_menu_index`）
- [[dicts/platform_product__wkfl_flag]]（`platform_product.wkfl_flag`）
- [[dicts/platform_product__enable]]（`platform_product.enable`）
- [[dicts/platform_product__app_tenant_code]]（`platform_product.app_tenant_code`）
- [[dicts/platform_product__db_tenant_code]]（`platform_product.db_tenant_code`）
- [[dicts/platform_product__act_procinst_status]]（`platform_product.act_procinst_status`）
- [[dicts/platform_product__general_flag]]（`platform_product.general_flag`）
