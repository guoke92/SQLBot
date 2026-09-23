---
type: table
title: 租户项目审批流程配置表
page_key: tenant_project_approval_flow_config
belong: tables
status: draft
anchors:
- tenant_project_approval_flow_config
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_config
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- tenant_project_approval
- tenant_project_approval_flow_config__is_optional
- tenant_project_approval_flow_config__is_operate
- tenant_project_approval_flow_config__enable
- tenant_project_approval_flow_config__flow_code
- tenant_project_approval_flow_config__node_code
---
# 租户项目审批流程配置表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow_config
database: lowcode_pplatform
desc: 租户项目审批流程配置表
inactive: false
primary_key:
- id
grain: 审批流程模板节点
name_anchors:
- node_name
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: flow_code
  type: string
  desc: 流程编码：NO_ONLINE，STANDARD，REGULAR
  dict:
  - REGULAR
  - STANDARD
  - NO_ONLINE
  label:
  - 常规项目流程
  - 标准项目流程
  - 无需上线审批
- name: node_code
  type: string
  desc: 节点编码字典
  dict: [PROJECT_CONFIG, OTHER, PROJECT_MANAGER, OPERATION, BUSINESS_MANAGER, LEGAL_REVIEW,
    LEGAL_PROCESS, SUPPLEMENT_AGREEMENT]
  label: [方案配置, 其他, 方案经理, 运营审批, 业务经理审批, 法务复核, 法务经办, 补充协议]
- name: node_name
  type: string
  desc: 节点名称（中文）
- name: node_order
  type: number
  desc: 节点顺序
- name: is_optional
  type: string
  desc: 是否可选节点：Y/N
  dict:
  - N
  - Y
  label:
  - 否
  - 是
- name: is_operate
  type: string
  desc: 是否可操作
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label:
  - 启用
  - 停用
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

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_config.flow_code
right: tenant_project_approval.flow_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
source: comment_fk
join_role: business_code
priority: primary
name_evidence:
  match: comment_fk
  stem: tenant_project_approval_flow_config
  comment: 流程配置编码（tenant_project_approval_flow_config#flow_code）
evidence: database_schema:tenant_project_approval.flow_code#comment_fk:tenant_project_approval_flow_config#flow_code
authenticity_note: comment_fk 保留；UAT empty_endpoint (tenant_project_approval.flow_code
  全 NULL)。 配置侧有 NO_ONLINE/STANDARD/REGULAR；有数据后再升 confirmed。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_config.code
right: tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: full_sweep:code_ref UAT empty
source: full_sweep
join_role: business_code
priority: secondary
authenticity_note: code:ref-convention
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]

### 概念

- [[concepts/online_approval_wf]]

### 字典

- [[dicts/tenant_project_approval_flow_config__flow_code]]（`tenant_project_approval_flow_config.flow_code`）
- [[dicts/tenant_project_approval_flow_config__node_code]]（`tenant_project_approval_flow_config.node_code`）
- [[dicts/tenant_project_approval_flow_config__is_optional]]（`tenant_project_approval_flow_config.is_optional`）
- [[dicts/tenant_project_approval_flow_config__is_operate]]（`tenant_project_approval_flow_config.is_operate`）
- [[dicts/tenant_project_approval_flow_config__enable]]（`tenant_project_approval_flow_config.enable`）
