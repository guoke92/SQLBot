---
type: table
title: 平台产品企业角色
page_key: platform_product_cust_role
belong: tables
status: draft
anchors: [platform_product_cust_role]
sources: ['database_schema:lowcode_pplatform.platform_product_cust_role']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, platform_product_cust_role__product_code, platform_product_cust_role__company_type_code,
  platform_product_cust_role__enable]
---

# 平台产品企业角色

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_role

`name`, `product_code`

### company_role

`company_type_code`, `company_type_name`

### tenant

`app_tenant_code`, `db_tenant_code`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`organization_id`

## 字段

```ground:table
table: platform_product_cust_role
database: lowcode_pplatform
description: 平台产品企业角色
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, company_type_code, company_type_name]
clusters:
- key: common
  title: 通用
  include: always
- key: product_role
  title: 产品与角色标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_cust_role
- key: company_role
  title: 企业角色
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_cust_role
- key: tenant
  title: 租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_cust_role
- key: act_procinst
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.platform_product_cust_role
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
  cluster: product_role
- name: product_code
  data_type: string
  description: 产品编码
  cluster: product_role
  dictionary: platform_product_cust_role__product_code
- name: company_type_code
  data_type: string
  description: 企业角色编码
  cluster: company_role
  dictionary: platform_product_cust_role__company_type_code
- name: company_type_name
  data_type: string
  description: 企业角色名称
  cluster: company_role
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: platform_product_cust_role__enable
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
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: platform_product_cust_role.product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.platform_product_cust_role.product_code;database_profile:lowcode_pplatform.platform_product_cust_role.product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 12
  miss: 12
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/platform_product_cust_role__product_code]]（`platform_product_cust_role.product_code`）
- [[dicts/platform_product_cust_role__company_type_code]]（`platform_product_cust_role.company_type_code`）
- [[dicts/platform_product_cust_role__enable]]（`platform_product_cust_role.enable`）
