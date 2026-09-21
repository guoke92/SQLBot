---
type: table
title: 平台产品企业角色
page_key: platform_product_cust_role
belong: tables
status: draft
anchors: [platform_product_cust_role]
sources: ['database_schema:lowcode_pplatform.platform_product_cust_role']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, platform_product_cust_role__product_code, platform_product_cust_role__company_type_code,
  platform_product_cust_role__enable]
---

# 平台产品企业角色

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: platform_product_cust_role
database: lowcode_pplatform
desc: 平台产品企业角色
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, company_type_code, company_type_name]
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
  desc: 名称
- name: product_code
  type: string
  desc: 产品编码
  dict: [VOUCHER, STORAGE, CROSSBORDER, RVSFACTOR_PC, ORDER, ACCOUNT_PRODUCT, ACFLOW,
    AMS, BEECREDIT, DEALER, DRAFTQA, DRAFT]
- name: company_type_code
  type: string
  desc: 企业角色编码
  dict: [CORE, SUPPLIER, PLATFORM_OPERATOR_COMPANY, FINANCE, PROJECT_COMPANY, CORPORATION_COMPANY,
    CORE_MANAGER, DEALER]
- name: company_type_name
  type: string
  desc: 企业角色名称
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
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
