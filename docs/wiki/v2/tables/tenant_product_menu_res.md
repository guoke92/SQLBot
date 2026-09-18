---
type: table
title: 租户产品菜单按钮表
page_key: tenant_product_menu_res
belong: tables
status: draft
anchors: [tenant_product_menu_res]
sources: ['database_schema:lowcode_pplatform.tenant_product_menu_res']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_product, tenant_product_menu, tenant_product_menu_res__product_code,
  tenant_product_menu_res__company_type, tenant_product_menu_res__enable]
---

# 租户产品菜单按钮表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_tenant

`product_code`, `company_type`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### menu_resource

`menu_id`, `resource_id`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: tenant_product_menu_res
database: lowcode_pplatform
description: 租户产品菜单按钮表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: product_tenant
  title: 产品与租户归属
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product_menu_res
- key: menu_resource
  title: 菜单与按钮资源
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product_menu_res
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_product_menu_res
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: product_code
  data_type: string
  description: 产品code
  cluster: product_tenant
  dictionary: tenant_product_menu_res__product_code
- name: company_type
  data_type: string
  description: 企业类型
  cluster: product_tenant
  dictionary: tenant_product_menu_res__company_type
- name: menu_id
  data_type: number
  description: 菜单ID
  cluster: menu_resource
- name: resource_id
  data_type: number
  description: 按钮ID
  cluster: menu_resource
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_product_menu_res__enable
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
  cluster: product_tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: product_tenant
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
  cluster: product_tenant
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: tenant_product.code
right: tenant_product_menu_res.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_product_menu_res.product_code;database_profile:lowcode_pplatform.tenant_product_menu_res.product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品code
overlap:
  probed: true
  ratio: 0.0
  sample_size: 2
  miss: 2
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 对端 tenant_product.code，name_evidence 为 family_suffix(stem=product)，注释「产品code」语义相关，但探测
  overlap ratio=0.0（sample=2，miss=2），值域不契合，故判 unlikely。
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: tenant_product_menu.id
right: tenant_product_menu_res.menu_id
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_product_menu_res.menu_id;database_profile:lowcode_pplatform.tenant_product_menu_res.menu_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: menu
  comment: 菜单ID
overlap:
  probed: true
  ratio: 0.0
  sample_size: 8
  miss: 8
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 对端 tenant_product_menu.id，列名/注释为菜单ID 家族关联，但探测 overlap ratio=0.0（sample=8，miss=8），值域不契合，维持
  unlikely。
```

## 页面链接

### 关联表

- [[tables/tenant_product]]
- [[tables/tenant_product_menu]]

### 字典

- [[dicts/tenant_product_menu_res__product_code]]（`tenant_product_menu_res.product_code`）
- [[dicts/tenant_product_menu_res__company_type]]（`tenant_product_menu_res.company_type`）
- [[dicts/tenant_product_menu_res__enable]]（`tenant_product_menu_res.enable`）
