---
type: table
title: 集团成员单位关系表
page_key: cust_group_rel
belong: tables
status: draft
anchors: [cust_group_rel]
sources: ['database_schema:lowcode_pplatform.cust_group_rel', 'code_path:CustCompanyQueryMapper.xml:112']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_group_rel__root_flag, cust_group_rel__level, cust_group_rel__status]
---

# 集团成员单位关系表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_group_rel
database: lowcode_pplatform
desc: 集团成员单位关系表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: cust_id
  type: number
  desc: 企业id
- name: parent_group_id
  type: number
  desc: 父id
- name: parent_cust_id
  type: number
  desc: 父企业id
- name: root_cust_id
  type: number
  desc: 根企业id
- name: root_group_id
  type: number
  desc: 根id
- name: root_flag
  type: string
  desc: 是否集团企业 Y:是 N:不是
  dict: [N, Y]
  label: [不是, 是]
- name: level
  type: number
  desc: 层级
  dict: ['1']
- name: cust_type
  type: string
  desc: 企业角色 多企业角色用逗号分隔
- name: status
  type: string
  desc: 状态 已生效:EFFECTIVE 未生效:INEFFECTIVE 已拒绝:REJECTED
  dict: [EFFECTIVE, INEFFECTIVE, REJECTED]
  label: [已生效, 未生效, 已拒绝]
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
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
default_filter:
  predicate: cust_group_rel.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustCompanyQueryMapper.xml:112
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_group_rel.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyQueryMapper.xml:109
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 200
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 集团关系 cust_id 是企业主键。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_group_rel__root_flag]]（`cust_group_rel.root_flag`）
- [[dicts/cust_group_rel__level]]（`cust_group_rel.level`）
- [[dicts/cust_group_rel__status]]（`cust_group_rel.status`）
