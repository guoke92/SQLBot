---
type: table
title: 客户操作运营变更记录
page_key: cust_oper_change_record
belong: tables
status: draft
anchors: [cust_oper_change_record]
sources: ['database_schema:lowcode_pplatform.cust_oper_change_record']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_person_info, cust_company_info, cust_oper_change_record__change_type,
  cust_oper_change_record__enable]
---

# 客户操作运营变更记录

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: cust_oper_change_record
database: lowcode_pplatform
desc: 客户操作运营变更记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [person_name, company_name, before_operator_name, after_operator_name,
  code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: person_id
  type: number
  desc: 企业联系人id
- name: person_name
  type: string
  desc: 联系人姓名
- name: company_id
  type: number
  desc: 企业ID
- name: company_name
  type: string
  desc: 企业名称
- name: company_code
  type: string
  desc: 企业编号
- name: before_operator_id
  type: string
  desc: 变更前运营人员ID
- name: before_operator_name
  type: string
  desc: 变更前运营人员姓名
- name: after_operator_id
  type: string
  desc: 变更后运营人员ID
- name: after_operator_name
  type: string
  desc: 变更后运营人员姓名
- name: change_type
  type: string
  desc: 变更类型
  dict: [BATCH, ASSET_AUDIT_SYNC, CUST_CHANGE_CALLBACK, MANUAL]
- name: change_reason
  type: string
  desc: 变更原因
- name: asset_id
  type: string
  desc: 资产id
- name: asset_no
  type: string
  desc: 资产编号
- name: source_system
  type: string
  desc: 来源系统
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
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

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_person_info.id
right: cust_oper_change_record.person_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_oper_change_record.person_id;database_profile:lowcode_pplatform.cust_oper_change_record.person_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: person
  comment: 企业联系人id
overlap:
  probed: true
  ratio: 0.9947
  sample_size: 190
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_oper_change_record.company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_oper_change_record.company_id;database_profile:lowcode_pplatform.cust_oper_change_record.company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业ID
overlap:
  probed: true
  ratio: 1.0
  sample_size: 97
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_oper_change_record.company_code
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_oper_change_record.company_code;database_profile:lowcode_pplatform.cust_oper_change_record.company_code
source: name
join_role: business_code
priority: secondary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业编号
overlap:
  probed: true
  ratio: 1.0
  sample_size: 97
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/cust_person_info]]
- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_oper_change_record__change_type]]（`cust_oper_change_record.change_type`）
- [[dicts/cust_oper_change_record__enable]]（`cust_oper_change_record.enable`）
