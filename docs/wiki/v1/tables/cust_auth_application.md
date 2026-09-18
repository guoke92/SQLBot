---
type: table
title: 客户产品开通表
page_key: cust_auth_application
belong: tables
status: draft
anchors: [cust_auth_application]
sources: ['database_schema:lowcode_pplatform.cust_auth_application']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, cust_company_info, tenant_product, cust_auth_application_config,
  cust_role_info, cust_auth_application__platform_product_code, cust_auth_application__enable,
  cust_auth_application__app_tenant_code, cust_auth_application__open_status]
---

# 客户产品开通表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### product

`name`, `platform_product_code`, `application`, `main_data_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### open

`open_status`, `open_time`

### customer_ref

`ref_cust_company_info`, `ref_parent_company`, `ref_cust_auth_application_tenant_product`

### org

`organization_id`, `cust_manager_id`

## 字段

```ground:table
table: cust_auth_application
database: lowcode_pplatform
description: 客户产品开通表
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
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: open
  title: 开通信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: customer_ref
  title: 关联引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
- key: org
  title: 组织机构与管理人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application
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
  description: 产品名称
  cluster: product
- name: platform_product_code
  data_type: string
  description: 平台产品编码
  cluster: product
  dictionary: cust_auth_application__platform_product_code
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_auth_application__enable
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
  cluster: common
  dictionary: cust_auth_application__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: org
- name: application
  data_type: string
  description: 产品应用
  cluster: product
- name: open_status
  data_type: string
  description: 开通状态
  cluster: open
  dictionary: cust_auth_application__open_status
- name: cust_manager_id
  data_type: number
  description: 企业管理员
  cluster: org
- name: open_time
  data_type: temporal
  description: 开通时间
  cluster: open
- name: ref_cust_company_info
  data_type: string
  description: 客户应用
  cluster: customer_ref
- name: ref_parent_company
  data_type: string
  description: 关联母公司
  cluster: customer_ref
- name: main_data_id
  data_type: number
  description: 主数据id
  cluster: product
- name: ref_cust_auth_application_tenant_product
  data_type: string
  description: 关联应用
  cluster: customer_ref
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: cust_auth_application.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_auth_application.platform_product_code;database_profile:lowcode_pplatform.cust_auth_application.platform_product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 6
  miss: 6
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 名称证据强（platform_product 精确表名 + 平台产品编码语义），但探针 6 条全 miss、overlap=0.0；样本偏小，暂判
  unlikely，建议复核双方编码口径。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_auth_application.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_auth_application.ref_cust_company_info;database_profile:lowcode_pplatform.cust_auth_application.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 客户应用
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名指向 cust_company_info（name_evidence=exact_table），但注释“客户应用”与客户公司语义有偏差，且探针
  200 条全 miss、overlap=0.0，判 unlikely。
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.id
right: cust_auth_application.ref_cust_auth_application_tenant_product
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_auth_application.ref_cust_auth_application_tenant_product;database_profile:lowcode_pplatform.cust_auth_application.ref_cust_auth_application_tenant_product
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_product
  comment: 关联应用
overlap:
  probed: true
  ratio: 0.0
  sample_size: 23
  miss: 23
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名为长引用（name_evidence=long_ref，含 tenant_product），探针 23 条全 miss、overlap=0.0，判
  unlikely。
```

## 页面链接

### 关联表

- [[tables/platform_product]]
- [[tables/cust_company_info]]
- [[tables/tenant_product]]
- [[tables/cust_auth_application_config]]
- [[tables/cust_role_info]]

### 字典

- [[dicts/cust_auth_application__platform_product_code]]（`cust_auth_application.platform_product_code`）
- [[dicts/cust_auth_application__enable]]（`cust_auth_application.enable`）
- [[dicts/cust_auth_application__app_tenant_code]]（`cust_auth_application.app_tenant_code`）
- [[dicts/cust_auth_application__open_status]]（`cust_auth_application.open_status`）
