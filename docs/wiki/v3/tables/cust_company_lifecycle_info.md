---
type: table
title: 企业生命周期记录
page_key: cust_company_lifecycle_info
belong: tables
status: draft
anchors: [cust_company_lifecycle_info]
sources: ['database_schema:lowcode_pplatform.cust_company_lifecycle_info']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_company_lifecycle_info__type, cust_company_lifecycle_info__enable]
---

# 企业生命周期记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_company_lifecycle_info
database: lowcode_pplatform
desc: 企业生命周期记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: company_id
  type: number
  desc: 企业id
- name: reason
  type: string
  desc: 冻结原因
- name: attach
  type: string
  desc: 冻结附件路径集合
- name: type
  type: string
  desc: 类型
  dict: [FRZ, UNFRZ]
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
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
- name: ref_cust_company_info
  type: string
  desc: 关联企业code
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_lifecycle_info.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyInfoApplication.java:7082
source: l1_code
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
authenticity_note: 冻结/解冻留痕按企业主键。预生成行 enable=N，确认后改 Y。ref_cust_company_info 本路径未使用。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_lifecycle_info.ref_cust_company_info
cardinality: one_to_many
trust: disputed
authenticity: unknown
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
sides:
- {source: l1_code, left: cust_company_info.id, right: cust_company_lifecycle_info.company_id,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_company_lifecycle_info.ref_cust_company_info,
  trust: proposed}
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_company_lifecycle_info__type]]（`cust_company_lifecycle_info.type`）
- [[dicts/cust_company_lifecycle_info__enable]]（`cust_company_lifecycle_info.enable`）
