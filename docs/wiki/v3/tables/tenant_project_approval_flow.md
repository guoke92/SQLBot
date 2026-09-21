---
type: table
title: 租户项目审批流程表
page_key: tenant_project_approval_flow
belong: tables
status: draft
anchors: [tenant_project_approval_flow]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow', 'code_path:ProjectApprovalApplication.java:571']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_project_approval_flow_node, tenant_project_approval_flow_config,
  tenant_project_approval_flow__node_code, tenant_project_approval_flow__node_order,
  tenant_project_approval_flow__node_status, tenant_project_approval_flow__is_optional,
  tenant_project_approval_flow__is_operate, tenant_project_approval_flow__enable]
---

# 租户项目审批流程表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow
database: lowcode_pplatform
desc: 租户项目审批流程表
inactive: false
primary_key: [id]
grain: 审批单节点实例，按 node_order
name_anchors: [node_name, approver_user_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: node_code
  type: string
  desc: 节点编码
  dict: [PROJECT_MANAGER, BUSINESS_MANAGER, OPERATION, PROJECT_CONFIG, LEGAL_PROCESS,
    LEGAL_REVIEW, OTHER, SUPPLEMENT_AGREEMENT]
  label: [方案经理, 业务经理审批, 运营审批, 方案配置, 法务经办, 法务复核, 其他, 补充协议]
- name: node_name
  type: string
  desc: 节点名称（中文）
- name: node_order
  type: number
  desc: 节点顺序，从 1 开始
  dict: ['1', '2', '3', '4', '5', '6']
  label: {'1': 开始}
- name: node_status
  type: string
  desc: 节点状态
  dict: [PENDING, APPROVED, APPROVING, REJECTED]
  label: [待审批, 已通过, 审批中, 已拒绝]
- name: is_optional
  type: string
  desc: 是否可选节点：Y/N
  dict: [N, Y]
- name: is_operate
  type: string
  desc: 是否可编辑
  dict: [Y, N]
- name: approver_user_id
  type: string
  desc: 审批人 userId
- name: approver_user_name
  type: string
  desc: 审批人姓名
- name: ref_tenant_project_approval_flow_tenant_project_approval
  type: string
  desc: 关联项目审批
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
default_filter:
  predicate: tenant_project_approval_flow.enable = 'Y'
  trust: confirmed
  evidence: code_path:ProjectApprovalApplication.java:571
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:571
source: l1_code
join_role: identity
priority: primary
authenticity_note: 流程节点按审批单 code，不是审批 id。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.id
right: tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval
cardinality: one_to_many
trust: disputed
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
sides:
- {source: l1_code, left: tenant_project_approval.code, right: tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval,
  trust: confirmed}
- {source: name, left: tenant_project_approval.id, right: tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval,
  trust: proposed}
```

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
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_node]]
- [[tables/tenant_project_approval_flow_config]]

### 字典

- [[dicts/tenant_project_approval_flow__node_code]]（`tenant_project_approval_flow.node_code`）
- [[dicts/tenant_project_approval_flow__node_order]]（`tenant_project_approval_flow.node_order`）
- [[dicts/tenant_project_approval_flow__node_status]]（`tenant_project_approval_flow.node_status`）
- [[dicts/tenant_project_approval_flow__is_optional]]（`tenant_project_approval_flow.is_optional`）
- [[dicts/tenant_project_approval_flow__is_operate]]（`tenant_project_approval_flow.is_operate`）
- [[dicts/tenant_project_approval_flow__enable]]（`tenant_project_approval_flow.enable`）
