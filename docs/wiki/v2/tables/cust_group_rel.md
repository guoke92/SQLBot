---
type: table
title: 集团成员单位关系表
page_key: cust_group_rel
belong: tables
status: draft
anchors: [cust_group_rel]
sources: ['database_schema:lowcode_pplatform.cust_group_rel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_group_rel__root_flag, cust_group_rel__level, cust_group_rel__status]
---

# 集团成员单位关系表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### group_hierarchy

`cust_id`, `parent_group_id`, `parent_cust_id`, `root_cust_id`, `root_group_id`, `root_flag`, `level`

### cust_role_status

`cust_type`, `status`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: cust_group_rel
database: lowcode_pplatform
description: 集团成员单位关系表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: group_hierarchy
  title: 集团层级关系
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: cust_role_status
  title: 企业角色与状态
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: cust_id
  data_type: number
  description: 企业id
  cluster: group_hierarchy
- name: parent_group_id
  data_type: number
  description: 父id
  cluster: group_hierarchy
- name: parent_cust_id
  data_type: number
  description: 父企业id
  cluster: group_hierarchy
- name: root_cust_id
  data_type: number
  description: 根企业id
  cluster: group_hierarchy
- name: root_group_id
  data_type: number
  description: 根id
  cluster: group_hierarchy
- name: root_flag
  data_type: string
  description: 是否集团企业 Y:是 N:不是
  cluster: group_hierarchy
  dictionary: cust_group_rel__root_flag
- name: level
  data_type: number
  description: 层级
  cluster: group_hierarchy
  dictionary: cust_group_rel__level
- name: cust_type
  data_type: string
  description: 企业角色 多企业角色用逗号分隔
  cluster: cust_role_status
- name: status
  data_type: string
  description: 状态 已生效:EFFECTIVE 未生效:INEFFECTIVE 已拒绝:REJECTED
  cluster: cust_role_status
  dictionary: cust_group_rel__status
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
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_group_rel.cust_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_group_rel.cust_id;database_profile:lowcode_pplatform.cust_group_rel.cust_id
source: name
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
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_group_rel__root_flag]]（`cust_group_rel.root_flag`）
- [[dicts/cust_group_rel__level]]（`cust_group_rel.level`）
- [[dicts/cust_group_rel__status]]（`cust_group_rel.status`）
