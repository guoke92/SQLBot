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
related: [cust_company_info, cust_auth_application, cust_role_info__enable, cust_role_info__app_tenant_code,
  cust_role_info__status, cust_role_info__role_type]
---

# 客户产品角色关联表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### role_info

`name`, `status`, `role_type`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### customer_link

`platform_cust_id`, `ref_cust_company_info`, `ref_cust_auth_application`

### org_master

`organization_id`, `main_data_id`

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
- key: role_info
  title: 角色信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: approval
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: customer_link
  title: 客户关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_role_info
- key: org_master
  title: 机构与主数据
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
  cluster: role_info
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
  dictionary: cust_role_info__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
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
  cluster: org_master
- name: status
  data_type: string
  description: 状态
  cluster: role_info
  dictionary: cust_role_info__status
- name: platform_cust_id
  data_type: number
  description: 关联平台企业ID
  cluster: customer_link
- name: ref_cust_company_info
  data_type: string
  description: 客户类型
  cluster: customer_link
- name: ref_cust_auth_application
  data_type: string
  description: 应用客户角色
  cluster: customer_link
- name: role_type
  data_type: string
  description: 角色类型
  cluster: role_info
  dictionary: cust_role_info__role_type
- name: main_data_id
  data_type: number
  description: 主数据id
  cluster: org_master
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
authenticity_note: 名称命中 cust_auth_application，但样本仅 1 行且未命中，证据不足，保留待人工核验。
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
authenticity_note: 名称命中 cust_company_info，但本地注释为“客户类型”而非外键语义，且 200 行探测全部未命中，判定 unlikely。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_auth_application]]

### 字典

- [[dicts/cust_role_info__enable]]（`cust_role_info.enable`）
- [[dicts/cust_role_info__app_tenant_code]]（`cust_role_info.app_tenant_code`）
- [[dicts/cust_role_info__status]]（`cust_role_info.status`）
- [[dicts/cust_role_info__role_type]]（`cust_role_info.role_type`）
