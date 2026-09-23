---
type: table
title: 租户项目审批流程文件表
page_key: tenant_project_approval_flow_file
belong: tables
status: draft
anchors:
- tenant_project_approval_flow_file
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_file
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- tenant_project_approval
- tenant_project_approval_flow_comment
- tenant_project_approval_flow_node
- tenant_project_approval_flow_file__enable
---
# 租户项目审批流程文件表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow_file
database: lowcode_pplatform
desc: 租户项目审批流程文件表
inactive: false
primary_key:
- id
grain: 审批附件
name_anchors:
- catg_name
- file_name
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: catg_id
  type: string
  desc: 影像分类编码
  dict:
  - FBP_OA_COMMENT_FILE
  - FBP_AGREEMENT
  - FBP_OA_ATTACHMENT
- name: catg_name
  type: string
  desc: 影像分类名称
- name: busi_key
  type: string
  desc: 业务key
- name: file_id
  type: string
  desc: 文件id
- name: file_name
  type: string
  desc: 文件名称
- name: file_url
  type: string
  desc: 文件url
- name: file_path
  type: string
  desc: 文件路径
- name: ref_tenant_project_approval_flow_file_project_approval_flow_node
  type: string
  desc: 关联项目流程节点
- name: ref_tenant_project_approval_flow_file_comment
  type: string
  desc: 关联项目审批
- name: ref_tenant_project_approval_flow_file_project_approval
  type: string
  desc: 关联项目审批
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
  label: [启用, 停用]
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

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.code
right: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalDeskApplication.java:966
source: l1_code
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_file_project_approval_flow_node
  comment: 关联项目流程节点
overlap:
  probed: true
  ratio: 1.0
  sample_size: 139
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 文件按 flow_node.code 关联。
```
```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_comment.code
right: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_comment
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1752
source: l1_code
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_file_comment
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 63
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 文件按 comment.getCode() 关联。
```
```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1753
source: l1_code
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_file_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 112
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 文件 ref 存 approval.getCode()。
```
## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_comment]]
- [[tables/tenant_project_approval_flow_node]]

### 字典

- [[dicts/tenant_project_approval_flow_file__catg_id]]（`tenant_project_approval_flow_file.catg_id`）
- [[dicts/tenant_project_approval_flow_file__enable]]（`tenant_project_approval_flow_file.enable`）
