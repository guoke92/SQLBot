---
type: table
title: 企业生命周期记录
page_key: cust_company_lifecycle_info
belong: tables
status: draft
anchors: [cust_company_lifecycle_info]
sources: ['database_schema:lowcode_pplatform.cust_company_lifecycle_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_company_lifecycle_info__type, cust_company_lifecycle_info__enable,
  cust_company_lifecycle_info__app_tenant_code]
---

# 企业生命周期记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`

### lifecycle

`company_id`, `reason`, `attach`, `type`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`, `ref_cust_company_info`

## 字段

```ground:table
table: cust_company_lifecycle_info
database: lowcode_pplatform
description: 企业生命周期记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 主档身份
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
- key: lifecycle
  title: 企业生命周期
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
- key: approval
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: company_id
  data_type: number
  description: 企业id
  cluster: lifecycle
- name: reason
  data_type: string
  description: 冻结原因
  cluster: lifecycle
- name: attach
  data_type: string
  description: 冻结附件路径集合
  cluster: lifecycle
- name: type
  data_type: string
  description: 类型
  cluster: lifecycle
  dictionary: cust_company_lifecycle_info__type
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: identity
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_company_lifecycle_info__enable
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
  dictionary: cust_company_lifecycle_info__app_tenant_code
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
- name: ref_cust_company_info
  data_type: string
  description: 关联企业code
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_lifecycle_info.company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info.company_id;database_profile:lowcode_pplatform.cust_company_lifecycle_info.company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 0.9143
  ratio_reverse: 0.0
  sample_size: 35
  miss: 3
  deepened: true
  query_ok: true
  authenticity: unknown
authenticity_note: name_evidence 为 family_suffix，本地注释企业id；overlap 正向 0.9143、样本35、miss3，反向
  0 符合子表多对一，判 likely。
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_lifecycle_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_company_lifecycle_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_company_lifecycle_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 关联企业code
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: name_evidence 为 exact_table，但本地注释为关联企业code，候选对端是 id，语义不匹配；overlap
  未取得有效比例，判 unlikely。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_company_lifecycle_info__type]]（`cust_company_lifecycle_info.type`）
- [[dicts/cust_company_lifecycle_info__enable]]（`cust_company_lifecycle_info.enable`）
- [[dicts/cust_company_lifecycle_info__app_tenant_code]]（`cust_company_lifecycle_info.app_tenant_code`）
