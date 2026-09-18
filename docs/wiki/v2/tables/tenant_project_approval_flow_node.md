---
type: table
title: 租户项目审批流程节点表
page_key: tenant_project_approval_flow_node
belong: tables
status: draft
anchors: [tenant_project_approval_flow_node]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_node']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval_flow, tenant_project_approval_flow_config, tenant_project_approval_flow_credit,
  tenant_project_approval_flow_file, tenant_project_approval, tenant_project_approval_flow_node__node_code,
  tenant_project_approval_flow_node__operate_type, tenant_project_approval_flow_node__approval_type,
  tenant_project_approval_flow_node__is_low_risk, tenant_project_approval_flow_node__enable,
  tenant_project_approval_flow_node__is_back_agreement]
---

# 租户项目审批流程节点表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### approval_node

`node_code`, `node_order`

### approval_action

`operate_type`, `approve_comment`, `operate_time`

### approval_attribute

`approval_type`, `is_low_risk`, `is_back_agreement`

### handler

`operator_user_id`, `operator_user_name`, `transfer_to_user_id`, `transfer_to_user_name`, `cc_user_id`

### approval_ref

`ref_tenant_project_approval_flow_node_project_approval`, `ref_tenant_project_approval_flow_node_project_approval_flow`

### process_instance

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_node
database: lowcode_pplatform
description: 租户项目审批流程节点表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [node_code, operator_user_name, transfer_to_user_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: approval_node
  title: 审批节点定义
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: approval_action
  title: 审批操作记录
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: approval_attribute
  title: 审批业务属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: handler
  title: 操作与转审人员
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: approval_ref
  title: 审批关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: process_instance
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: node_code
  data_type: string
  description: 节点编码
  cluster: approval_node
  dictionary: tenant_project_approval_flow_node__node_code
- name: node_order
  data_type: number
  description: 审批顺序，从1开始
  cluster: approval_node
- name: operate_type
  data_type: string
  description: 操作类型
  cluster: approval_action
  dictionary: tenant_project_approval_flow_node__operate_type
- name: approval_type
  data_type: string
  description: 审批类型
  cluster: approval_attribute
  dictionary: tenant_project_approval_flow_node__approval_type
- name: is_low_risk
  data_type: string
  description: 是否低风险项目
  cluster: approval_attribute
  dictionary: tenant_project_approval_flow_node__is_low_risk
- name: approve_comment
  data_type: string
  description: 审批意见
  cluster: approval_action
- name: operator_user_id
  data_type: string
  description: 操作人 userId
  cluster: handler
- name: operator_user_name
  data_type: string
  description: 操作人姓名
  cluster: handler
- name: transfer_to_user_id
  data_type: string
  description: 被转审人id
  cluster: handler
- name: transfer_to_user_name
  data_type: string
  description: 被转审人name
  cluster: handler
- name: cc_user_id
  data_type: string
  description: 抄送相关人员userId列表(JSON数组)
  cluster: handler
- name: operate_time
  data_type: temporal
  description: 操作时间
  cluster: approval_action
- name: ref_tenant_project_approval_flow_node_project_approval
  data_type: string
  description: 关联项目审批
  cluster: approval_ref
- name: ref_tenant_project_approval_flow_node_project_approval_flow
  data_type: string
  description: 关联项目审批流程
  cluster: approval_ref
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
  dictionary: tenant_project_approval_flow_node__enable
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
- name: is_back_agreement
  data_type: string
  description: 是否后补合作协议
  cluster: approval_attribute
  dictionary: tenant_project_approval_flow_node__is_back_agreement
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
authenticity_note: overlap ratio=1.0（sample 127，miss 0），且本列注释『关联项目审批』明确表达指向项目审批表的关联语义，值域契合+注释关联
  → likely。
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
authenticity_note: overlap ratio=1.0（sample 172，miss 0），本列注释『关联项目审批流程』明确指向审批流程表，值域契合+注释关联
  → likely。
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
- [[dicts/tenant_project_approval_flow_node__operate_type]]（`tenant_project_approval_flow_node.operate_type`）
- [[dicts/tenant_project_approval_flow_node__approval_type]]（`tenant_project_approval_flow_node.approval_type`）
- [[dicts/tenant_project_approval_flow_node__is_low_risk]]（`tenant_project_approval_flow_node.is_low_risk`）
- [[dicts/tenant_project_approval_flow_node__enable]]（`tenant_project_approval_flow_node.enable`）
- [[dicts/tenant_project_approval_flow_node__is_back_agreement]]（`tenant_project_approval_flow_node.is_back_agreement`）
