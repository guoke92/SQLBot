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
related: [tenant_project_approval, tenant_project_approval_flow_file, tenant_project_approval_flow_comment__ref_tenant_project_approval_flow_comment_approval,
  tenant_project_approval_flow_comment__enable, tenant_project_approval_flow_comment__app_tenant_code,
  tenant_project_approval_flow_comment__db_tenant_code]
---

# 租户项目审批备注信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant_scope

`app_tenant_code`, `db_tenant_code`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### comment_info

`content`, `cc_user_id`

### business_ref

`ref_tenant_project_approval_flow_comment_approval`, `organization_id`

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
- key: tenant_scope
  title: 租户与环境
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: approval_flow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: comment_info
  title: 备注与抄送
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
- key: business_ref
  title: 业务关联
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
  cluster: comment_info
- name: cc_user_id
  data_type: string
  description: 抄送相关人员
  cluster: comment_info
- name: ref_tenant_project_approval_flow_comment_approval
  data_type: string
  description: 关联项目审批
  cluster: business_ref
  dictionary: tenant_project_approval_flow_comment__ref_tenant_project_approval_flow_comment_approval
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_scope
  dictionary: tenant_project_approval_flow_comment__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_scope
  dictionary: tenant_project_approval_flow_comment__db_tenant_code
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
  cluster: business_ref
```

## 关联关系

### likely — 值域支持较强

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
overlap:
  probed: true
  ratio: 1.0
  sample_size: 22
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 对端 tenant_project_approval.code：name_evidence 无字面匹配（match=none），但
  overlap 探针比值 1.0（22/22、miss 0），与本地注释「关联项目审批」相符，判为 likely；该列为外键引用列，非主引用边不在此判定。
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_file]]

### 字典

- [[dicts/tenant_project_approval_flow_comment__ref_tenant_project_approval_flow_comment_approval]]（`tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval`）
- [[dicts/tenant_project_approval_flow_comment__enable]]（`tenant_project_approval_flow_comment.enable`）
- [[dicts/tenant_project_approval_flow_comment__app_tenant_code]]（`tenant_project_approval_flow_comment.app_tenant_code`）
- [[dicts/tenant_project_approval_flow_comment__db_tenant_code]]（`tenant_project_approval_flow_comment.db_tenant_code`）
