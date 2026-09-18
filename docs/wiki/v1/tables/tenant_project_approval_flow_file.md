---
type: table
title: 租户项目审批流程文件表
page_key: tenant_project_approval_flow_file
belong: tables
status: draft
anchors: [tenant_project_approval_flow_file]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_file']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval_flow_node, tenant_project_approval_flow_comment,
  tenant_project_approval, tenant_project_approval_flow_file__catg_id, tenant_project_approval_flow_file__enable,
  tenant_project_approval_flow_file__app_tenant_code, tenant_project_approval_flow_file__db_tenant_code]
---

# 租户项目审批流程文件表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `busi_key`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### catg

`catg_id`, `catg_name`

### file

`file_id`, `file_name`, `file_url`, `file_path`

### approval_ref

`ref_tenant_project_approval_flow_file_project_approval_flow_node`, `ref_tenant_project_approval_flow_file_comment`, `ref_tenant_project_approval_flow_file_project_approval`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_file
database: lowcode_pplatform
description: 租户项目审批流程文件表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [catg_name, file_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: catg
  title: 影像分类
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: file
  title: 文件信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: approval_ref
  title: 审批关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: act_procinst
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
- key: tenant
  title: 租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_file
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: catg_id
  data_type: string
  description: 影像分类编码
  cluster: catg
  dictionary: tenant_project_approval_flow_file__catg_id
- name: catg_name
  data_type: string
  description: 影像分类名称
  cluster: catg
- name: busi_key
  data_type: string
  description: 业务key
  cluster: common
- name: file_id
  data_type: string
  description: 文件id
  cluster: file
- name: file_name
  data_type: string
  description: 文件名称
  cluster: file
- name: file_url
  data_type: string
  description: 文件url
  cluster: file
- name: file_path
  data_type: string
  description: 文件路径
  cluster: file
- name: ref_tenant_project_approval_flow_file_project_approval_flow_node
  data_type: string
  description: 关联项目流程节点
  cluster: approval_ref
- name: ref_tenant_project_approval_flow_file_comment
  data_type: string
  description: 关联项目审批
  cluster: approval_ref
- name: ref_tenant_project_approval_flow_file_project_approval
  data_type: string
  description: 关联项目审批
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
  dictionary: tenant_project_approval_flow_file__enable
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
  dictionary: tenant_project_approval_flow_file__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: tenant_project_approval_flow_file__db_tenant_code
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
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.code
right: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
overlap:
  probed: true
  ratio: 1.0
  sample_size: 139
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 名称无直接证据，但关联项目流程节点注释与 100% 覆盖支持该外键关联。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_comment.code
right: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_comment
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_comment
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
overlap:
  probed: true
  ratio: 1.0
  sample_size: 63
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 名称无直接证据，但关联项目审批注释与 100% 覆盖支持该外键关联。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
overlap:
  probed: true
  ratio: 1.0
  sample_size: 112
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 名称无直接证据，但关联项目审批注释与 100% 覆盖支持该外键关联。
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval_flow_node]]
- [[tables/tenant_project_approval_flow_comment]]
- [[tables/tenant_project_approval]]

### 字典

- [[dicts/tenant_project_approval_flow_file__catg_id]]（`tenant_project_approval_flow_file.catg_id`）
- [[dicts/tenant_project_approval_flow_file__enable]]（`tenant_project_approval_flow_file.enable`）
- [[dicts/tenant_project_approval_flow_file__app_tenant_code]]（`tenant_project_approval_flow_file.app_tenant_code`）
- [[dicts/tenant_project_approval_flow_file__db_tenant_code]]（`tenant_project_approval_flow_file.db_tenant_code`）
