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
  tenant_project_approval__sp_no, tenant_project_approval__project_type, tenant_project_approval__simple_mode,
  tenant_project_approval__wf_status, tenant_project_approval__is_low_risk, tenant_project_approval__is_latest,
  tenant_project_approval__enable, tenant_project_approval__app_tenant_code, tenant_project_approval__db_tenant_code,
  tenant_project_approval__is_add]
---

# 租户项目审批表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### approval_doc

`approval_no`, `is_online_approval`, `related_approval_no`, `sp_no`, `is_latest`, `is_add`

### solution

`solution_manager_id`, `solution_manager_name`

### project

`project_type`, `simple_mode`, `project_plan`, `is_low_risk`

### initiator

`initiator_user_id`, `initiator_user_name`, `initiate_time`

### workflow

`wf_procdef_key`, `wf_status`, `wf_last_operator_id`, `wf_last_operator`, `wf_last_operate_time`, `flow_code`

### counterparty

`core_enterprise_names`, `capital_names`, `whitelist_query_result`

### ref_tenant

`ref_tenant_project_approval_tenant_project`, `ref_tenant_project_approval_tenant_project_approval_flow_config`, `ref_tenant_project_approval_tenant_project_approval`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `complete_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

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
- key: approval_doc
  title: 审批单据标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: solution
  title: 方案经理
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: project
  title: 项目属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: initiator
  title: 发起人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: workflow
  title: 工作流
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: counterparty
  title: 核心企业与资金方
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: ref_tenant
  title: 关联引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: act_procinst
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval
- key: tenant
  title: 租户隔离
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
  cluster: approval_doc
- name: is_online_approval
  data_type: string
  description: 是否发起上线审批：Y/N
  cluster: approval_doc
  dictionary: tenant_project_approval__is_online_approval
- name: related_approval_no
  data_type: string
  description: 关联审批编号
  cluster: approval_doc
- name: sp_no
  data_type: string
  description: 立项审批编号（wechat_project_approval_apply#sp_no）
  cluster: approval_doc
  dictionary: tenant_project_approval__sp_no
- name: solution_manager_id
  data_type: string
  description: 方案经理 userId
  cluster: solution
- name: solution_manager_name
  data_type: string
  description: 方案经理姓名
  cluster: solution
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
  cluster: initiator
- name: initiator_user_name
  data_type: string
  description: 发起人姓名
  cluster: initiator
- name: initiate_time
  data_type: temporal
  description: 发起时间
  cluster: initiator
- name: wf_procdef_key
  data_type: string
  description: 工作流流程定义key
  cluster: workflow
- name: wf_status
  data_type: string
  description: 工作流状态
  cluster: workflow
  dictionary: tenant_project_approval__wf_status
- name: wf_last_operator_id
  data_type: string
  description: 工作流最近操作人ID
  cluster: workflow
- name: wf_last_operator
  data_type: string
  description: 工作流最近操作人
  cluster: workflow
- name: wf_last_operate_time
  data_type: temporal
  description: 工作流最近操作时间
  cluster: workflow
- name: is_low_risk
  data_type: string
  description: 是否低风险项目:Y,N
  cluster: project
  dictionary: tenant_project_approval__is_low_risk
- name: flow_code
  data_type: string
  description: 流程配置编码（tenant_project_approval_flow_config#flow_code）
  cluster: workflow
- name: is_latest
  data_type: string
  description: 是否最新审批
  cluster: approval_doc
  dictionary: tenant_project_approval__is_latest
- name: core_enterprise_names
  data_type: string
  description: 核心企业名称(JSON格式字符串，含order字段标记顺序)
  cluster: counterparty
- name: capital_names
  data_type: string
  description: 资金方名称(JSON格式字符串，含order字段标记顺序)
  cluster: counterparty
- name: whitelist_query_result
  data_type: string
  description: 白名单查询结果(JSON，提交后锁定)
  cluster: counterparty
- name: ref_tenant_project_approval_tenant_project
  data_type: string
  description: 关联租户项目
  cluster: ref_tenant
- name: ref_tenant_project_approval_tenant_project_approval_flow_config
  data_type: string
  description: 关联租户项目流程配置
  cluster: ref_tenant
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
  cluster: act_procinst
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
  dictionary: tenant_project_approval__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: tenant_project_approval__db_tenant_code
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
- name: ref_tenant_project_approval_tenant_project_approval
  data_type: string
  description: 关联原审批数据
  cluster: ref_tenant
- name: complete_time
  data_type: temporal
  description: 完成时间
  cluster: act_procinst
- name: is_add
  data_type: string
  description: 是否新增项目；Y=是，N=否
  cluster: approval_doc
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
authenticity_note: 名称族 flow 对码；但本列注释指向 tenant_project_approval_flow_config#flow_code，与候选对端表
  tenant_project_approval_flow 不一致，且 overlap 未探明（样本 0），需人工确认父表。
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
authenticity_note: 列名与注释都指向流程配置表，名称证据较强；但未探测到重叠（样本 0），真实性待人工确认。
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
authenticity_note: 长引用名指向租户项目，但 200 样本重叠率 0，引用列可能存编码或其他键。
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
- [[dicts/tenant_project_approval__sp_no]]（`tenant_project_approval.sp_no`）
- [[dicts/tenant_project_approval__project_type]]（`tenant_project_approval.project_type`）
- [[dicts/tenant_project_approval__simple_mode]]（`tenant_project_approval.simple_mode`）
- [[dicts/tenant_project_approval__wf_status]]（`tenant_project_approval.wf_status`）
- [[dicts/tenant_project_approval__is_low_risk]]（`tenant_project_approval.is_low_risk`）
- [[dicts/tenant_project_approval__is_latest]]（`tenant_project_approval.is_latest`）
- [[dicts/tenant_project_approval__enable]]（`tenant_project_approval.enable`）
- [[dicts/tenant_project_approval__app_tenant_code]]（`tenant_project_approval.app_tenant_code`）
- [[dicts/tenant_project_approval__db_tenant_code]]（`tenant_project_approval.db_tenant_code`）
- [[dicts/tenant_project_approval__is_add]]（`tenant_project_approval.is_add`）
