---
type: table
title: 租户项目审批流程节点表
page_key: tenant_project_approval_flow_node
belong: tables
status: draft
anchors: [tenant_project_approval_flow_node]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_node']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval_flow, tenant_project_approval_flow_config, tenant_project_approval_flow_credit,
  tenant_project_approval_flow_file, tenant_project_approval, tenant_project_approval_flow_node__node_code,
  tenant_project_approval_flow_node__node_order, tenant_project_approval_flow_node__operate_type,
  tenant_project_approval_flow_node__approval_type, tenant_project_approval_flow_node__is_low_risk,
  tenant_project_approval_flow_node__enable, tenant_project_approval_flow_node__is_back_agreement]
---

# 租户项目审批流程节点表

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow_node
database: lowcode_pplatform
desc: 租户项目审批流程节点表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [node_code, operator_user_name, transfer_to_user_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: node_code
  type: string
  desc: 节点编码
  dict: [PROJECT_MANAGER, PROJECT_CONFIG, BUSINESS_MANAGER, OPERATION, LEGAL_PROCESS,
    LEGAL_REVIEW]
- name: node_order
  type: number
  desc: 审批顺序，从1开始
  dict: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
    '15', '16']
- name: operate_type
  type: string
  desc: 操作类型
  dict: [pass, back, reject, delegate, revoke]
- name: approval_type
  type: string
  desc: 审批类型
  dict: [ONLINE_APPROVAL, BACK_AGREEMENT]
- name: is_low_risk
  type: string
  desc: 是否低风险项目
  dict: [Y, N]
- name: approve_comment
  type: string
  desc: 审批意见
- name: operator_user_id
  type: string
  desc: 操作人 userId
- name: operator_user_name
  type: string
  desc: 操作人姓名
- name: transfer_to_user_id
  type: string
  desc: 被转审人id
- name: transfer_to_user_name
  type: string
  desc: 被转审人name
- name: cc_user_id
  type: string
  desc: 抄送相关人员userId列表(JSON数组)
- name: operate_time
  type: temporal
  desc: 操作时间
- name: ref_tenant_project_approval_flow_node_project_approval
  type: string
  desc: 关联项目审批
- name: ref_tenant_project_approval_flow_node_project_approval_flow
  type: string
  desc: 关联项目审批流程
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
- name: is_back_agreement
  type: string
  desc: 是否后补合作协议
  dict: [Y, N]
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_node_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 127
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow.code
right: tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_node_project_approval_flow
  comment: 关联项目审批流程
overlap:
  probed: true
  ratio: 1.0
  sample_size: 172
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval_flow]]
- [[tables/tenant_project_approval_flow_config]]
- [[tables/tenant_project_approval_flow_credit]]
- [[tables/tenant_project_approval_flow_file]]
- [[tables/tenant_project_approval]]

### 字典

- [[dicts/tenant_project_approval_flow_node__node_code]]（`tenant_project_approval_flow_node.node_code`）
- [[dicts/tenant_project_approval_flow_node__node_order]]（`tenant_project_approval_flow_node.node_order`）
- [[dicts/tenant_project_approval_flow_node__operate_type]]（`tenant_project_approval_flow_node.operate_type`）
- [[dicts/tenant_project_approval_flow_node__approval_type]]（`tenant_project_approval_flow_node.approval_type`）
- [[dicts/tenant_project_approval_flow_node__is_low_risk]]（`tenant_project_approval_flow_node.is_low_risk`）
- [[dicts/tenant_project_approval_flow_node__enable]]（`tenant_project_approval_flow_node.enable`）
- [[dicts/tenant_project_approval_flow_node__is_back_agreement]]（`tenant_project_approval_flow_node.is_back_agreement`）
