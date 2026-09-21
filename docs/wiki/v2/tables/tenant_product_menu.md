---
type: table
title: 租户产品菜单表
page_key: tenant_product_menu
belong: tables
status: draft
anchors: [tenant_product_menu]
sources: ['database_schema:lowcode_pplatform.tenant_product_menu']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_product, tenant_product_menu_res, tenant_product_menu__product_code,
  tenant_product_menu__company_type, tenant_product_menu__enable]
---

# 租户产品菜单表

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: tenant_product_menu
database: lowcode_pplatform
desc: 租户产品菜单表
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
  desc: 名称
- name: product_code
  type: string
  desc: 产品code
  dict: [RVSFACTOR_PC, BEECREDIT, ACCOUNT_PRODUCT]
- name: company_type
  type: string
  desc: 企业角色
  dict: [CORE, SUPPLIER, FINANCE, PROJECT_COMPANY, PLATFORM_OPERATOR_COMPANY, CORPORATION_COMPANY,
    PLATFORM_OPERATOR, DEALER, CORE_MANAGER]
- name: menu_id
  type: number
  desc: 菜单id
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
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: tenant_product.code
right: tenant_product_menu.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_product_menu.product_code;database_profile:lowcode_pplatform.tenant_product_menu.product_code
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
```

## 页面链接

### 关联表

- [[tables/tenant_product]]
- [[tables/tenant_product_menu_res]]

### 字典

- [[dicts/tenant_product_menu__product_code]]（`tenant_product_menu.product_code`）
- [[dicts/tenant_product_menu__company_type]]（`tenant_product_menu.company_type`）
- [[dicts/tenant_product_menu__enable]]（`tenant_product_menu.enable`）
