---
type: table
title: 用户企业角色
page_key: cust_user_rel
belong: tables
status: draft
anchors: [cust_user_rel]
sources: ['database_schema:lowcode_pplatform.cust_user_rel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_user_rel__code, cust_user_rel__company_type, cust_user_rel__type_status,
  cust_user_rel__user_type, cust_user_rel__enable]
---

# 用户企业角色

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### user

`user_id`, `user_type`

### company

`company_id`, `company_name`, `company_type`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`type_status`, `organization_id`

## 字段

```ground:table
table: cust_user_rel
database: lowcode_pplatform
description: 用户企业角色
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, company_name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: user
  title: 用户/联系人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: company
  title: 企业信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_user_rel
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
  dictionary: cust_user_rel__code
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: user_id
  data_type: number
  description: 用户id
  cluster: user
- name: company_id
  data_type: number
  description: 企业id
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  cluster: company
- name: company_type
  data_type: string
  description: 企业类型
  cluster: company
  dictionary: cust_user_rel__company_type
- name: type_status
  data_type: string
  description: 客户角色
  dictionary: cust_user_rel__type_status
- name: user_type
  data_type: string
  description: 联系人类型
  cluster: user
  dictionary: cust_user_rel__user_type
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_user_rel__enable
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

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_user_rel.company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_user_rel.company_id;database_profile:lowcode_pplatform.cust_user_rel.company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 1
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: name_evidence 为 family_suffix（company ↔ company_id），本地注释「企业id」与对端企业主档语义一致；overlap
  探测 ratio=1.0 但 sample_size=1、deepened=false，数值证据极弱，仅凭命名与注释判为 likely，待人工/更多样本确认。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_user_rel__code]]（`cust_user_rel.code`）
- [[dicts/cust_user_rel__company_type]]（`cust_user_rel.company_type`）
- [[dicts/cust_user_rel__type_status]]（`cust_user_rel.type_status`）
- [[dicts/cust_user_rel__user_type]]（`cust_user_rel.user_type`）
- [[dicts/cust_user_rel__enable]]（`cust_user_rel.enable`）
