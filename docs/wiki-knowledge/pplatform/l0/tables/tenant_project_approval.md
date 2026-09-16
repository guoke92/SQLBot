---
type: table
title: 租户项目审批表
page_key: tenant_project_approval
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval
sources:
- database_schema:lowcode_pplatform.tenant_project_approval
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### approval_core

`approval_no`, `related_approval_no`, `sp_no`, `wf_procdef_key`, `flow_code`, `act_procinst_id`, `act_procinst_no`

### project

`project_type`, `simple_mode`, `project_plan`, `is_low_risk`, `is_latest`, `core_enterprise_names`, `capital_names`, `whitelist_query_result`, `is_add`

### participants

`solution_manager_id`, `solution_manager_name`, `initiator_user_id`, `initiator_user_name`, `wf_last_operator_id`, `wf_last_operator`

### workflow_status_time

`is_online_approval`, `initiate_time`, `wf_status`, `wf_last_operate_time`, `act_procinst_status`, `act_procinst_date`, `complete_time`

### tenant_org_ref

`ref_tenant_project_approval_tenant_project`, `ref_tenant_project_approval_tenant_project_approval_flow_config`, `app_tenant_code`, `db_tenant_code`, `organization_id`, `ref_tenant_project_approval_tenant_project_approval`

### misc

`name`, `remark`

## 字段

```ground:table
table: tenant_project_approval
database: lowcode_pplatform
description: 租户项目审批表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- solution_manager_name
- initiator_user_name
- flow_code
- code
- name
clusters:
- key: common
  title: 通用审计与编码
  include: always
- key: approval_core
  title: 审批与流程标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: project
  title: 项目属性
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: participants
  title: 相关人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: workflow_status_time
  title: 审批状态与时间
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: tenant_org_ref
  title: 租户与关联引用
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: misc
  title: 名称备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: approval_no
  data_type: string
  description: 审批编号，格式：SX+yyyymmdd+xxx
  nullable: true
  cluster: approval_core
- name: is_online_approval
  data_type: string
  description: 是否发起上线审批：Y/N
  nullable: true
  cluster: workflow_status_time
  dictionary: tenant_project_approval_is_online_approval
- name: related_approval_no
  data_type: string
  description: 关联审批编号
  nullable: true
  cluster: approval_core
- name: sp_no
  data_type: string
  description: 立项审批编号（wechat_project_approval_apply#sp_no）
  nullable: true
  cluster: approval_core
- name: solution_manager_id
  data_type: string
  description: 方案经理 userId
  nullable: true
  cluster: participants
- name: solution_manager_name
  data_type: string
  description: 方案经理姓名
  nullable: true
  cluster: participants
- name: project_type
  data_type: string
  description: 项目类型：STANDARD（标准） / REGULAR（常规）
  nullable: true
  cluster: project
  dictionary: tenant_project_approval_project_type
- name: simple_mode
  data_type: string
  description: 是否为简易模式项目/常规非低风险项目，Y/N
  nullable: true
  cluster: project
  dictionary: tenant_project_approval_simple_mode
- name: project_plan
  data_type: string
  description: 项目方案描述
  nullable: true
  cluster: project
- name: initiator_user_id
  data_type: string
  description: 发起人 userId
  nullable: true
  cluster: participants
- name: initiator_user_name
  data_type: string
  description: 发起人姓名
  nullable: true
  cluster: participants
- name: initiate_time
  data_type: temporal
  description: 发起时间
  nullable: true
  cluster: workflow_status_time
- name: wf_procdef_key
  data_type: string
  description: 工作流流程定义key
  nullable: true
  cluster: approval_core
- name: wf_status
  data_type: string
  description: 工作流状态
  nullable: true
  cluster: workflow_status_time
  dictionary: tenant_project_approval_wf_status
- name: wf_last_operator_id
  data_type: string
  description: 工作流最近操作人ID
  nullable: true
  cluster: participants
- name: wf_last_operator
  data_type: string
  description: 工作流最近操作人
  nullable: true
  cluster: participants
- name: wf_last_operate_time
  data_type: temporal
  description: 工作流最近操作时间
  nullable: true
  cluster: workflow_status_time
- name: is_low_risk
  data_type: string
  description: 是否低风险项目:Y,N
  nullable: true
  cluster: project
  dictionary: tenant_project_approval_is_low_risk
- name: flow_code
  data_type: string
  description: 流程配置编码（tenant_project_approval_flow_config#flow_code）
  nullable: true
  cluster: approval_core
- name: is_latest
  data_type: string
  description: 是否最新审批
  nullable: true
  cluster: project
  dictionary: tenant_project_approval_is_latest
- name: core_enterprise_names
  data_type: string
  description: 核心企业名称(JSON格式字符串，含order字段标记顺序)
  nullable: true
  cluster: project
- name: capital_names
  data_type: string
  description: 资金方名称(JSON格式字符串，含order字段标记顺序)
  nullable: true
  cluster: project
- name: whitelist_query_result
  data_type: string
  description: 白名单查询结果(JSON，提交后锁定)
  nullable: true
  cluster: project
- name: ref_tenant_project_approval_tenant_project
  data_type: string
  description: 关联租户项目
  nullable: true
  cluster: tenant_org_ref
- name: ref_tenant_project_approval_tenant_project_approval_flow_config
  data_type: string
  description: 关联租户项目流程配置
  nullable: true
  cluster: tenant_org_ref
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: misc
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_project_approval_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: misc
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
  cluster: approval_core
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant_org_ref
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_org_ref
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval_core
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow_status_time
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow_status_time
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_org_ref
- name: ref_tenant_project_approval_tenant_project_approval
  data_type: string
  description: 关联原审批数据
  nullable: true
  cluster: tenant_org_ref
- name: complete_time
  data_type: temporal
  description: 完成时间
  nullable: true
  cluster: workflow_status_time
- name: is_add
  data_type: string
  description: 是否新增项目；Y=是，N=否
  nullable: true
  cluster: project
  dictionary: tenant_project_approval_is_add
```
