---
type: table
title: 租户项目审批流程节点表
page_key: tenant_project_approval_flow_node
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_node
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_node
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批流程节点表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### node_def

`node_code`, `node_order`, `name`, `remark`

### approval_action

`operate_type`, `approval_type`, `approve_comment`, `operator_user_id`, `operator_user_name`, `operate_time`

### transfer_cc

`transfer_to_user_id`, `transfer_to_user_name`, `cc_user_id`

### project_flag

`is_low_risk`, `is_back_agreement`

### procinst_ref

`ref_tenant_project_approval_flow_node_project_approval`, `ref_tenant_project_approval_flow_node_project_approval_flow`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_node
database: lowcode_pplatform
description: 租户项目审批流程节点表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- node_code
- operator_user_name
- transfer_to_user_name
- code
- name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: node_def
  title: 流程节点定义
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: approval_action
  title: 审批操作记录
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: transfer_cc
  title: 转审与抄送
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: project_flag
  title: 项目属性开关
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: procinst_ref
  title: 流程实例与关联单
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_node
- key: tenant_org
  title: 租户与机构
  confidence: proposed
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
  nullable: true
  cluster: node_def
  dictionary: tenant_project_approval_flow_node_node_code
- name: node_order
  data_type: number
  description: 审批顺序，从1开始
  nullable: true
  cluster: node_def
- name: operate_type
  data_type: string
  description: 操作类型
  nullable: true
  cluster: approval_action
  dictionary: tenant_project_approval_flow_node_operate_type
- name: approval_type
  data_type: string
  description: 审批类型
  nullable: true
  cluster: approval_action
  dictionary: tenant_project_approval_flow_node_approval_type
- name: is_low_risk
  data_type: string
  description: 是否低风险项目
  nullable: true
  cluster: project_flag
  dictionary: tenant_project_approval_flow_node_is_low_risk
- name: approve_comment
  data_type: string
  description: 审批意见
  nullable: true
  cluster: approval_action
- name: operator_user_id
  data_type: string
  description: 操作人 userId
  nullable: true
  cluster: approval_action
- name: operator_user_name
  data_type: string
  description: 操作人姓名
  nullable: true
  cluster: approval_action
- name: transfer_to_user_id
  data_type: string
  description: 被转审人id
  nullable: true
  cluster: transfer_cc
- name: transfer_to_user_name
  data_type: string
  description: 被转审人name
  nullable: true
  cluster: transfer_cc
- name: cc_user_id
  data_type: string
  description: 抄送相关人员userId列表(JSON数组)
  nullable: true
  cluster: transfer_cc
- name: operate_time
  data_type: temporal
  description: 操作时间
  nullable: true
  cluster: approval_action
- name: ref_tenant_project_approval_flow_node_project_approval
  data_type: string
  description: 关联项目审批
  nullable: true
  cluster: procinst_ref
- name: ref_tenant_project_approval_flow_node_project_approval_flow
  data_type: string
  description: 关联项目审批流程
  nullable: true
  cluster: procinst_ref
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: node_def
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_project_approval_flow_node_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: node_def
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: procinst_ref
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_org
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: procinst_ref
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: procinst_ref
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: procinst_ref
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_org
- name: is_back_agreement
  data_type: string
  description: 是否后补合作协议
  nullable: true
  cluster: project_flag
  dictionary: tenant_project_approval_flow_node_is_back_agreement
```
