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
related: [cust_company_info, cust_group_rel__root_flag, cust_group_rel__level, cust_group_rel__cust_type,
  cust_group_rel__status, cust_group_rel__enable, cust_group_rel__app_tenant_code,
  cust_group_rel__db_tenant_code]
---

# 集团成员单位关系表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### group_rel

`cust_id`, `parent_group_id`, `parent_cust_id`, `root_cust_id`, `root_group_id`, `level`

### group_attr

`root_flag`, `cust_type`, `status`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### audit

（空）

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
- key: group_rel
  title: 集团成员关系
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: group_attr
  title: 集团属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_group_rel
- key: audit
  title: 审计信息
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
  cluster: group_rel
- name: parent_group_id
  data_type: number
  description: 父id
  cluster: group_rel
- name: parent_cust_id
  data_type: number
  description: 父企业id
  cluster: group_rel
- name: root_cust_id
  data_type: number
  description: 根企业id
  cluster: group_rel
- name: root_group_id
  data_type: number
  description: 根id
  cluster: group_rel
- name: root_flag
  data_type: string
  description: 是否集团企业 Y:是 N:不是
  cluster: group_attr
  dictionary: cust_group_rel__root_flag
- name: level
  data_type: number
  description: 层级
  cluster: group_rel
  dictionary: cust_group_rel__level
- name: cust_type
  data_type: string
  description: 企业角色 多企业角色用逗号分隔
  cluster: group_attr
  dictionary: cust_group_rel__cust_type
- name: status
  data_type: string
  description: 状态 已生效:EFFECTIVE 未生效:INEFFECTIVE 已拒绝:REJECTED
  cluster: group_attr
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
  dictionary: cust_group_rel__enable
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
  cluster: tenant_org
  dictionary: cust_group_rel__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
  dictionary: cust_group_rel__db_tenant_code
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
  cluster: tenant_org
```

## 关联关系

### likely — 值域支持较强

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
authenticity_note: cust_company_info.id ← cust_group_rel.cust_id：name_evidence 为 family_hub（stem=cust，注释「企业id」），overlap
  已探测 ratio=1.0（sample=200，miss=0），双向证据一致，判定 likely；仍需人工确认是否为主引用。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_group_rel__root_flag]]（`cust_group_rel.root_flag`）
- [[dicts/cust_group_rel__level]]（`cust_group_rel.level`）
- [[dicts/cust_group_rel__cust_type]]（`cust_group_rel.cust_type`）
- [[dicts/cust_group_rel__status]]（`cust_group_rel.status`）
- [[dicts/cust_group_rel__enable]]（`cust_group_rel.enable`）
- [[dicts/cust_group_rel__app_tenant_code]]（`cust_group_rel.app_tenant_code`）
- [[dicts/cust_group_rel__db_tenant_code]]（`cust_group_rel.db_tenant_code`）
