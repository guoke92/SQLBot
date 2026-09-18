---
type: table
title: 租户项目审批表
page_key: tenant_project_approval
belong: tables
status: draft
anchors: [tenant_project_approval]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project, tenant_project_approval_flow, tenant_project_approval_flow_config,
  tenant_project_approval_business_info, tenant_project_approval_flow_comment, tenant_project_approval_flow_credit,
  tenant_project_approval_flow_file, tenant_project_approval_flow_node, tenant_project_approval__is_online_approval,
  tenant_project_approval__project_type, tenant_project_approval__simple_mode, tenant_project_approval__wf_status,
  tenant_project_approval__is_low_risk, tenant_project_approval__is_latest, tenant_project_approval__enable,
  tenant_project_approval__is_add]
---

# 租户项目审批表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### approval_flow

`approval_no`, `is_online_approval`, `related_approval_no`, `sp_no`, `initiate_time`, `wf_procdef_key`, `wf_status`, `wf_last_operate_time`, `flow_code`, `is_latest`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `complete_time`

### people

`solution_manager_id`, `solution_manager_name`, `initiator_user_id`, `initiator_user_name`, `wf_last_operator_id`, `wf_last_operator`

### project

`project_type`, `simple_mode`, `project_plan`, `is_low_risk`, `is_add`

### party

`core_enterprise_names`, `capital_names`, `whitelist_query_result`

### relation_ref

`ref_tenant_project_approval_tenant_project`, `ref_tenant_project_approval_tenant_project_approval_flow_config`, `organization_id`, `ref_tenant_project_approval_tenant_project_approval`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: tenant_project_approval
database: lowcode_pplatform
description: 租户项目审批表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [solution_manager_name, initiator_user_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: approval_flow
  title: 审批流程与状态
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: people
  title: 相关业务人员
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: project
  title: 项目属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: party
  title: 参与方与白名单
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: relation_ref
  title: 关联引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: tenant
  title: 租户标识
  trust: proposed
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
  cluster: approval_flow
- name: is_online_approval
  data_type: string
  description: 是否发起上线审批：Y/N
  cluster: approval_flow
  dictionary: tenant_project_approval__is_online_approval
- name: related_approval_no
  data_type: string
  description: 关联审批编号
  cluster: approval_flow
- name: sp_no
  data_type: string
  description: 立项审批编号（wechat_project_approval_apply#sp_no）
  cluster: approval_flow
- name: solution_manager_id
  data_type: string
  description: 方案经理 userId
  cluster: people
- name: solution_manager_name
  data_type: string
  description: 方案经理姓名
  cluster: people
- name: project_type
  data_type: string
  description: 项目类型：STANDARD（标准） / REGULAR（常规）
  cluster: project
  dictionary: tenant_project_approval__project_type
- name: simple_mode
  data_type: string
  description: 是否为简易模式项目/常规非低风险项目，Y/N
  cluster: project
  dictionary: tenant_project_approval__simple_mode
- name: project_plan
  data_type: string
  description: 项目方案描述
  cluster: project
- name: initiator_user_id
  data_type: string
  description: 发起人 userId
  cluster: people
- name: initiator_user_name
  data_type: string
  description: 发起人姓名
  cluster: people
- name: initiate_time
  data_type: temporal
  description: 发起时间
  cluster: approval_flow
- name: wf_procdef_key
  data_type: string
  description: 工作流流程定义key
  cluster: approval_flow
- name: wf_status
  data_type: string
  description: 工作流状态
  cluster: approval_flow
  dictionary: tenant_project_approval__wf_status
- name: wf_last_operator_id
  data_type: string
  description: 工作流最近操作人ID
  cluster: people
- name: wf_last_operator
  data_type: string
  description: 工作流最近操作人
  cluster: people
- name: wf_last_operate_time
  data_type: temporal
  description: 工作流最近操作时间
  cluster: approval_flow
- name: is_low_risk
  data_type: string
  description: 是否低风险项目:Y,N
  cluster: project
  dictionary: tenant_project_approval__is_low_risk
- name: flow_code
  data_type: string
  description: 流程配置编码（tenant_project_approval_flow_config#flow_code）
  cluster: approval_flow
- name: is_latest
  data_type: string
  description: 是否最新审批
  cluster: approval_flow
  dictionary: tenant_project_approval__is_latest
- name: core_enterprise_names
  data_type: string
  description: 核心企业名称(JSON格式字符串，含order字段标记顺序)
  cluster: party
- name: capital_names
  data_type: string
  description: 资金方名称(JSON格式字符串，含order字段标记顺序)
  cluster: party
- name: whitelist_query_result
  data_type: string
  description: 白名单查询结果(JSON，提交后锁定)
  cluster: party
- name: ref_tenant_project_approval_tenant_project
  data_type: string
  description: 关联租户项目
  cluster: relation_ref
- name: ref_tenant_project_approval_tenant_project_approval_flow_config
  data_type: string
  description: 关联租户项目流程配置
  cluster: relation_ref
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
  dictionary: tenant_project_approval__enable
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
  cluster: approval_flow
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
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: relation_ref
- name: ref_tenant_project_approval_tenant_project_approval
  data_type: string
  description: 关联原审批数据
  cluster: relation_ref
- name: complete_time
  data_type: temporal
  description: 完成时间
  cluster: approval_flow
- name: is_add
  data_type: string
  description: 是否新增项目；Y=是，N=否
  cluster: project
  dictionary: tenant_project_approval__is_add
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow.code
right: tenant_project_approval.flow_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_project_approval.flow_code;database_profile:lowcode_pplatform.tenant_project_approval.flow_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: flow
  comment: 流程配置编码（tenant_project_approval_flow_config#flow_code）
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_config.id
right: tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config;database_profile:lowcode_pplatform.tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_project_approval_flow_config
  comment: 关联租户项目流程配置
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: tenant_project_approval.ref_tenant_project_approval_tenant_project
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project_approval.ref_tenant_project_approval_tenant_project;database_profile:lowcode_pplatform.tenant_project_approval.ref_tenant_project_approval_tenant_project
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_project
  comment: 关联租户项目
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/tenant_project]]
- [[tables/tenant_project_approval_flow]]
- [[tables/tenant_project_approval_flow_config]]
- [[tables/tenant_project_approval_business_info]]
- [[tables/tenant_project_approval_flow_comment]]
- [[tables/tenant_project_approval_flow_credit]]
- [[tables/tenant_project_approval_flow_file]]
- [[tables/tenant_project_approval_flow_node]]

### 字典

- [[dicts/tenant_project_approval__is_online_approval]]（`tenant_project_approval.is_online_approval`）
- [[dicts/tenant_project_approval__project_type]]（`tenant_project_approval.project_type`）
- [[dicts/tenant_project_approval__simple_mode]]（`tenant_project_approval.simple_mode`）
- [[dicts/tenant_project_approval__wf_status]]（`tenant_project_approval.wf_status`）
- [[dicts/tenant_project_approval__is_low_risk]]（`tenant_project_approval.is_low_risk`）
- [[dicts/tenant_project_approval__is_latest]]（`tenant_project_approval.is_latest`）
- [[dicts/tenant_project_approval__enable]]（`tenant_project_approval.enable`）
- [[dicts/tenant_project_approval__is_add]]（`tenant_project_approval.is_add`）
