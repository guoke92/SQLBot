---
type: table
title: 平台产品企业角色
page_key: platform_product_cust_role
belong: tables
status: draft
anchors:
- platform_product_cust_role
sources:
- database_schema:lowcode_pplatform.platform_product_cust_role
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- platform_product
- tenant_product
- platform_product_cust_role__enable
---
# 平台产品企业角色

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: platform_product_cust_role
database: lowcode_pplatform
desc: 平台产品企业角色
inactive: false
primary_key:
- id
grain: 平台产品适配的企业角色
name_anchors:
- code
- name
- company_type_code
- company_type_name
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
- name: company_type_code
  type: string
  desc: 企业角色编码
  dict:
  - CORE
  - SUPPLIER
  - PLATFORM_OPERATOR_COMPANY
  - FINANCE
  - PROJECT_COMPANY
  - CORPORATION_COMPANY
  - CORE_MANAGER
  - DEALER
- name: company_type_name
  type: string
  desc: 企业角色名称
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
left: platform_product.product_code
right: platform_product_cust_role.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_shared_domain;code contains-filter
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: 产品角色配置↔平台产品业务码
```
```ground:relation
type: EQUI_JOIN
left: tenant_product.platform_product_code
right: platform_product_cust_role.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_shared_domain L→R=1;user code filter
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: 内存 contains 同值域可 EQUI
```

## 页面链接

### 关联表

- [[tables/platform_product]]
- [[tables/tenant_product]]

### 字典

- [[dicts/platform_product_cust_role__company_type_code]]（`platform_product_cust_role.company_type_code`）
- [[dicts/platform_product_cust_role__enable]]（`platform_product_cust_role.enable`）
