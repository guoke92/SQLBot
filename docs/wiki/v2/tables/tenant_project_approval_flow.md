---
type: table
title: 租户项目审批流程表
page_key: tenant_project_approval_flow
belong: tables
status: draft
anchors: [tenant_project_approval_flow]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_project_approval_flow_node, tenant_project_approval_flow_config,
  tenant_project_approval_flow__node_code, tenant_project_approval_flow__node_status,
  tenant_project_approval_flow__is_optional, tenant_project_approval_flow__is_operate,
  tenant_project_approval_flow__enable]
---

# 租户项目审批流程表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### node

`node_code`, `node_name`, `node_order`, `node_status`, `is_optional`, `is_operate`

### approver

`approver_user_id`, `approver_user_name`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`ref_tenant_project_approval_flow_tenant_project_approval`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow
database: lowcode_pplatform
description: 租户项目审批流程表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [node_name, approver_user_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: node
  title: 审批节点
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: approver
  title: 审批人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: act_procinst
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: node_code
  data_type: string
  description: 节点编码
  cluster: node
  dictionary: tenant_project_approval_flow__node_code
- name: node_name
  data_type: string
  description: 节点名称（中文）
  cluster: node
- name: node_order
  data_type: number
  description: 节点顺序，从 1 开始
  cluster: node
- name: node_status
  data_type: string
  description: 节点状态
  cluster: node
  dictionary: tenant_project_approval_flow__node_status
- name: is_optional
  data_type: string
  description: 是否可选节点：Y/N
  cluster: node
  dictionary: tenant_project_approval_flow__is_optional
- name: is_operate
  data_type: string
  description: 是否可编辑
  cluster: node
  dictionary: tenant_project_approval_flow__is_operate
- name: approver_user_id
  data_type: string
  description: 审批人 userId
  cluster: approver
- name: approver_user_name
  data_type: string
  description: 审批人姓名
  cluster: approver
- name: ref_tenant_project_approval_flow_tenant_project_approval
  data_type: string
  description: 关联项目审批
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
  dictionary: tenant_project_approval_flow__enable
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

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.code
right: tenant_project_approval_flow.node_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow.node_code;database_profile:lowcode_pplatform.tenant_project_approval_flow.node_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: node
  comment: 节点编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 6
  miss: 6
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 名称证据为同族后缀（node.code ↔ node_code），但探测 overlap 比 0.0（6 值全 miss），值域不契合，判
  unlikely，保留待人工复核。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.id
right: tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval;database_profile:lowcode_pplatform.tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 0.0
  sample_size: 100
  miss: 100
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 注释「关联项目审批」与长引用列名指向 tenant_project_approval 主键，但探测 100 抽样 overlap
  全 miss（ratio 0.0），值域不契合，判 unlikely。
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_node]]
- [[tables/tenant_project_approval_flow_config]]

### 字典

- [[dicts/tenant_project_approval_flow__node_code]]（`tenant_project_approval_flow.node_code`）
- [[dicts/tenant_project_approval_flow__node_status]]（`tenant_project_approval_flow.node_status`）
- [[dicts/tenant_project_approval_flow__is_optional]]（`tenant_project_approval_flow.is_optional`）
- [[dicts/tenant_project_approval_flow__is_operate]]（`tenant_project_approval_flow.is_operate`）
- [[dicts/tenant_project_approval_flow__enable]]（`tenant_project_approval_flow.enable`）
