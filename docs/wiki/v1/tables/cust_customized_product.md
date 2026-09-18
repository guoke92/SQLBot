---
type: table
title: 客户快捷入口配置
page_key: cust_customized_product
belong: tables
status: draft
anchors: [cust_customized_product]
sources: ['database_schema:lowcode_pplatform.cust_customized_product']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_interworking_product, cust_project_rel, cust_customized_product__code,
  cust_customized_product__enable, cust_customized_product__app_tenant_code, cust_customized_product__db_tenant_code]
---

# 客户快捷入口配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_identity

`name`

### entry_display

`url`, `logo_icon_url`, `view_order`

### owner

`cust_id`, `ref_cust_customized_product_cust_company_info`, `organization_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: cust_customized_product
database: lowcode_pplatform
description: 客户快捷入口配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: product_identity
  title: 产品标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
- key: entry_display
  title: 入口展示
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
- key: owner
  title: 归属主体
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_customized_product
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
  dictionary: cust_customized_product__code
- name: name
  data_type: string
  description: 产品名称
  cluster: product_identity
- name: cust_id
  data_type: number
  description: 企业id
  cluster: owner
- name: url
  data_type: string
  description: 跳转链接
  cluster: entry_display
- name: logo_icon_url
  data_type: string
  description: 图标
  cluster: entry_display
- name: view_order
  data_type: number
  description: 显示顺序
  cluster: entry_display
- name: ref_cust_customized_product_cust_company_info
  data_type: string
  description: 客户关联自定义产品配置
  cluster: owner
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_customized_product__enable
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
  dictionary: cust_customized_product__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: cust_customized_product__db_tenant_code
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
  cluster: owner
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_customized_product.cust_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_customized_product.cust_id;database_profile:lowcode_pplatform.cust_customized_product.cust_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 15
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 列名/注释『企业id』直指企业主档，overlap 包含率 1.0（样本 15，miss 0），可判为指向 cust_company_info.id
  的有效关联。
```

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_customized_product.ref_cust_customized_product_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_customized_product.ref_cust_customized_product_cust_company_info;database_profile:lowcode_pplatform.cust_customized_product.ref_cust_customized_product_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_company_info
  comment: 客户关联自定义产品配置
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 列名为长引用式命名且注释提到客户关联配置，疑似指向 cust_company_info，但探测样本为 0、未取到重叠率，无法证实，保留待人工确认。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_interworking_product]]
- [[tables/cust_project_rel]]

### 字典

- [[dicts/cust_customized_product__code]]（`cust_customized_product.code`）
- [[dicts/cust_customized_product__enable]]（`cust_customized_product.enable`）
- [[dicts/cust_customized_product__app_tenant_code]]（`cust_customized_product.app_tenant_code`）
- [[dicts/cust_customized_product__db_tenant_code]]（`cust_customized_product.db_tenant_code`）
