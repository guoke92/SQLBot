---
type: table
title: 租户项目审批流程配置表
page_key: tenant_project_approval_flow_config
belong: tables
status: draft
anchors: [tenant_project_approval_flow_config]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_config']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_project_approval_flow, tenant_project_approval_flow_node,
  tenant_project_approval_flow_config__flow_code, tenant_project_approval_flow_config__node_code,
  tenant_project_approval_flow_config__node_name, tenant_project_approval_flow_config__node_order,
  tenant_project_approval_flow_config__is_optional, tenant_project_approval_flow_config__is_operate,
  tenant_project_approval_flow_config__enable]
---

# 租户项目审批流程配置表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### node

`node_code`, `node_name`, `node_order`, `is_optional`, `is_operate`

### process_instance

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`flow_code`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_config
database: lowcode_pplatform
description: 租户项目审批流程配置表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [node_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config
- key: node
  title: 审批节点
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config
- key: process_instance
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: flow_code
  data_type: string
  description: 流程编码：NO_ONLINE，STANDARD，REGULAR
  dictionary: tenant_project_approval_flow_config__flow_code
- name: node_code
  data_type: string
  description: 节点编码字典
  cluster: node
  dictionary: tenant_project_approval_flow_config__node_code
- name: node_name
  data_type: string
  description: 节点名称（中文）
  cluster: node
  dictionary: tenant_project_approval_flow_config__node_name
- name: node_order
  data_type: number
  description: 节点顺序
  cluster: node
  dictionary: tenant_project_approval_flow_config__node_order
- name: is_optional
  data_type: string
  description: 是否可选节点：Y/N
  cluster: node
  dictionary: tenant_project_approval_flow_config__is_optional
- name: is_operate
  data_type: string
  description: 是否可操作
  cluster: node
  dictionary: tenant_project_approval_flow_config__is_operate
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
  dictionary: tenant_project_approval_flow_config__enable
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
  cluster: process_instance
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
  cluster: process_instance
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: process_instance
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: process_instance
- name: organization_id
  data_type: string
  description: 机构编号
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow.code
right: tenant_project_approval_flow_config.flow_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config.flow_code;database_profile:lowcode_pplatform.tenant_project_approval_flow_config.flow_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: flow
  comment: 流程编码：NO_ONLINE，STANDARD，REGULAR
overlap:
  probed: true
  ratio: 0.0
  sample_size: 3
  miss: 3
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 名称仅 family_suffix 弱匹配；overlap 探测 ratio=0.0（3/3 miss），当前证据不支持连接。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.code
right: tenant_project_approval_flow_config.node_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config.node_code;database_profile:lowcode_pplatform.tenant_project_approval_flow_config.node_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: node
  comment: 节点编码字典
overlap:
  probed: true
  ratio: 0.0
  sample_size: 7
  miss: 7
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 名称仅 family_suffix 弱匹配；overlap 探测 ratio=0.0（7/7 miss），当前证据不支持连接。
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow]]
- [[tables/tenant_project_approval_flow_node]]

### 字典

- [[dicts/tenant_project_approval_flow_config__flow_code]]（`tenant_project_approval_flow_config.flow_code`）
- [[dicts/tenant_project_approval_flow_config__node_code]]（`tenant_project_approval_flow_config.node_code`）
- [[dicts/tenant_project_approval_flow_config__node_name]]（`tenant_project_approval_flow_config.node_name`）
- [[dicts/tenant_project_approval_flow_config__node_order]]（`tenant_project_approval_flow_config.node_order`）
- [[dicts/tenant_project_approval_flow_config__is_optional]]（`tenant_project_approval_flow_config.is_optional`）
- [[dicts/tenant_project_approval_flow_config__is_operate]]（`tenant_project_approval_flow_config.is_operate`）
- [[dicts/tenant_project_approval_flow_config__enable]]（`tenant_project_approval_flow_config.enable`）
