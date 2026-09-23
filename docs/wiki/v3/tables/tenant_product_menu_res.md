---
type: table
title: 租户产品菜单按钮表
page_key: tenant_product_menu_res
belong: tables
status: draft
anchors:
- tenant_product_menu_res
sources:
- database_schema:lowcode_pplatform.tenant_product_menu_res
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- tenant_product_menu
- tenant_product_menu_res__company_type
- tenant_product_menu_res__enable
---
# 租户产品菜单按钮表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_product_menu_res
database: lowcode_pplatform
desc: 租户产品菜单按钮表
inactive: false
primary_key:
- id
grain: 租户产品菜单按钮
name_anchors:
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: product_code
  type: string
  desc: 产品code
- name: company_type
  type: string
  desc: 企业类型
  dict:
  - CORPORATION_COMPANY
  - PLATFORM_OPERATOR_COMPANY
  - CORE
  - SUPPLIER
- name: menu_id
  type: number
  desc: 菜单ID
- name: resource_id
  type: number
  desc: 按钮ID
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label: [启用, 停用]
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

```ground:relation
type: EQUI_JOIN
left: tenant_product_menu.menu_id
right: tenant_product_menu_res.menu_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:菜单与按钮同 menu_id
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 菜单与按钮同 menu_id
```
```ground:relation
type: EQUI_JOIN
left: tenant_product_menu.product_code
right: tenant_product_menu_res.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:菜单与按钮同 product_code
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 菜单与按钮同 product_code
```

## 页面链接

### 关联表

- [[tables/tenant_product_menu]]

### 概念

- [[concepts/tenant_menu_product_code_term]]

### 字典

- [[dicts/tenant_product_menu_res__company_type]]（`tenant_product_menu_res.company_type`）
- [[dicts/tenant_product_menu_res__enable]]（`tenant_product_menu_res.enable`）
