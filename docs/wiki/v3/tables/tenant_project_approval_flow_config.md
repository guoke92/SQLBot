---
type: table
title: 租户项目审批流程配置表
page_key: tenant_project_approval_flow_config
belong: tables
status: draft
anchors: [tenant_project_approval_flow_config]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_config']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_project_approval_flow, tenant_project_approval_flow_node,
  tenant_project_approval_flow_config__flow_code, tenant_project_approval_flow_config__node_code,
  tenant_project_approval_flow_config__node_order, tenant_project_approval_flow_config__is_optional,
  tenant_project_approval_flow_config__is_operate, tenant_project_approval_flow_config__enable]
---

# 租户项目审批流程配置表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow_config
database: lowcode_pplatform
desc: 租户项目审批流程配置表
inactive: false
primary_key: [id]
grain: 审批流程模板节点
name_anchors: [node_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: flow_code
  type: string
  desc: 流程编码：NO_ONLINE，STANDARD，REGULAR
  dict: [REGULAR, STANDARD, NO_ONLINE]
  label: [常规项目流程, 标准项目流程, 无需上线审批]
- name: node_code
  type: string
  desc: 节点编码字典
  dict: [PROJECT_CONFIG, OTHER, PROJECT_MANAGER, OPERATION, BUSINESS_MANAGER, LEGAL_REVIEW,
    LEGAL_PROCESS]
  label: {PROJECT_CONFIG: 方案配置, PROJECT_MANAGER: 方案经理, OPERATION: 运营审批, BUSINESS_MANAGER: 业务经理审批,
    LEGAL_REVIEW: 法务复核, LEGAL_PROCESS: 法务经办}
- name: node_name
  type: string
  desc: 节点名称（中文）
- name: node_order
  type: number
  desc: 节点顺序
  dict: ['1', '2', '3', '4', '5', '6', '7']
- name: is_optional
  type: string
  desc: 是否可选节点：Y/N
  dict: [N, Y]
- name: is_operate
  type: string
  desc: 是否可操作
  dict: [Y, N]
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
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow]]
- [[tables/tenant_project_approval_flow_node]]

### 字典

- [[dicts/tenant_project_approval_flow_config__flow_code]]（`tenant_project_approval_flow_config.flow_code`）
- [[dicts/tenant_project_approval_flow_config__node_code]]（`tenant_project_approval_flow_config.node_code`）
- [[dicts/tenant_project_approval_flow_config__node_order]]（`tenant_project_approval_flow_config.node_order`）
- [[dicts/tenant_project_approval_flow_config__is_optional]]（`tenant_project_approval_flow_config.is_optional`）
- [[dicts/tenant_project_approval_flow_config__is_operate]]（`tenant_project_approval_flow_config.is_operate`）
- [[dicts/tenant_project_approval_flow_config__enable]]（`tenant_project_approval_flow_config.enable`）
