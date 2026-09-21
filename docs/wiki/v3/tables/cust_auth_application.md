---
type: table
title: 客户产品开通表
page_key: cust_auth_application
belong: tables
status: draft
anchors: [cust_auth_application]
sources: ['database_schema:lowcode_pplatform.cust_auth_application', 'code_path:CustAuthApplicationDaoImpl.java:75']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, cust_company_info, tenant_product, cust_auth_application_config,
  cust_role_info, cust_auth_application__platform_product_code, cust_auth_application__enable,
  cust_auth_application__open_status]
---

# 客户产品开通表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_auth_application
database: lowcode_pplatform
desc: 客户产品开通表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 产品名称
- name: platform_product_code
  type: string
  desc: 平台产品编码
  dict: [ACFLOW, RVSFACTOR_PC, ORDER, BEECREDIT, DRAFTQA, VOUCHER, STORAGE, DRAFT]
- name: enable
  type: string
  desc: enable
  dict: [Y]
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: application
  type: string
  desc: 产品应用
- name: open_status
  type: string
  desc: 开通状态
  dict: [OPENING, OPENED, NOT_OPENED]
  label: [开通中, 已开通, 未开通]
- name: cust_manager_id
  type: number
  desc: 企业管理员
- name: open_time
  type: temporal
  desc: 开通时间
- name: ref_cust_company_info
  type: string
  desc: 客户应用
- name: ref_parent_company
  type: string
  desc: 关联母公司
- name: main_data_id
  type: number
  desc: 主数据id
- name: ref_cust_auth_application_tenant_product
  type: string
  desc: 关联应用
default_filter:
  predicate: cust_auth_application.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustAuthApplicationDaoImpl.java:75
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_auth_application.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustAuthApplicationDaoImpl.java:73
source: l1_code
join_role: identity
priority: primary
authenticity_note: 产品开通按企业 code 关联，不是 id。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_auth_application.ref_cust_company_info
cardinality: one_to_many
trust: disputed
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
sides:
- {source: l1_code, left: cust_company_info.code, right: cust_auth_application.ref_cust_company_info,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_auth_application.ref_cust_company_info,
  trust: proposed}
```

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
- [[dicts/cust_auth_application__open_status]]（`cust_auth_application.open_status`）
