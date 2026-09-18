---
type: table
title: 客户产品角色关联表
page_key: cust_role_info
belong: tables
status: draft
anchors: [cust_role_info]
sources: ['database_schema:lowcode_pplatform.cust_role_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_auth_application, cust_role_info__enable, cust_role_info__status,
  cust_role_info__role_type]
---

# 客户产品角色关联表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### cust_ref

`organization_id`, `platform_cust_id`, `ref_cust_company_info`, `ref_cust_auth_application`, `main_data_id`

### role_status

`status`, `role_type`

## 字段

```ground:table
table: cust_role_info
database: lowcode_pplatform
description: 客户产品角色关联表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: act_procinst
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: cust_ref
  title: 客户主体引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: role_status
  title: 角色与状态
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
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
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_role_info__enable
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
  cluster: cust_ref
- name: status
  data_type: string
  description: 状态
  cluster: role_status
  dictionary: cust_role_info__status
- name: platform_cust_id
  data_type: number
  description: 关联平台企业ID
  cluster: cust_ref
- name: ref_cust_company_info
  data_type: string
  description: 客户类型
  cluster: cust_ref
- name: ref_cust_auth_application
  data_type: string
  description: 应用客户角色
  cluster: cust_ref
- name: role_type
  data_type: string
  description: 角色类型
  cluster: role_status
  dictionary: cust_role_info__role_type
- name: main_data_id
  data_type: number
  description: 主数据id
  cluster: cust_ref
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: cust_auth_application.id
right: cust_role_info.ref_cust_auth_application
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_role_info.ref_cust_auth_application;database_profile:lowcode_pplatform.cust_role_info.ref_cust_auth_application
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_auth_application
  comment: 应用客户角色
overlap:
  probed: true
  ratio: 0.0
  sample_size: 1
  miss: 1
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 表名精确匹配且本地注释「应用客户角色」与目标表（客户产品开通表）语义相关，但 overlap 仅探测 1 条样本且 ratio=0.0，样本量不足不能作为否定或肯定依据，维持
  unknown。
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_role_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_role_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_role_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 客户类型
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: name_evidence 仅为表名精确匹配（ref_cust_company_info ≈ cust_company_info），但本地注释为「客户类型」，与指向企业主档表的语义不符；overlap
  已探测 200 条全 miss（ratio=0.0），值域不契合，判 unlikely。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_auth_application]]

### 字典

- [[dicts/cust_role_info__enable]]（`cust_role_info.enable`）
- [[dicts/cust_role_info__status]]（`cust_role_info.status`）
- [[dicts/cust_role_info__role_type]]（`cust_role_info.role_type`）
