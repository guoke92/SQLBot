---
type: table
title: 租户项目审批备注信息
page_key: tenant_project_approval_flow_comment
belong: tables
status: draft
anchors: [tenant_project_approval_flow_comment]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_comment']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_project_approval_flow_file, tenant_project_approval_flow_comment__enable]
---

# 租户项目审批备注信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### comment_ref

`content`, `cc_user_id`, `ref_tenant_project_approval_flow_comment_approval`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_comment
database: lowcode_pplatform
description: 租户项目审批备注信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: comment_ref
  title: 备注与关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: act_procinst
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: content
  data_type: string
  description: 备注内容
  cluster: comment_ref
- name: cc_user_id
  data_type: string
  description: 抄送相关人员
  cluster: comment_ref
- name: ref_tenant_project_approval_flow_comment_approval
  data_type: string
  description: 关联项目审批
  cluster: comment_ref
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
  dictionary: tenant_project_approval_flow_comment__enable
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
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
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
  cluster: tenant_org
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_comment_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 22
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_file]]

### 字典

- [[dicts/tenant_project_approval_flow_comment__enable]]（`tenant_project_approval_flow_comment.enable`）
