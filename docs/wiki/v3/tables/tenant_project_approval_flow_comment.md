---
type: table
title: 租户项目审批备注信息
page_key: tenant_project_approval_flow_comment
belong: tables
status: draft
anchors:
- tenant_project_approval_flow_comment
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_comment
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- tenant_project_approval
- tenant_project_approval_flow_file
- tenant_project_approval_flow_comment__enable
---

# 租户项目审批备注信息

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow_comment
database: lowcode_pplatform
desc: 租户项目审批备注信息
inactive: false
primary_key:
- id
grain: 审批备注；apaas 有 @TableName DO，业务侧少直接引用
name_anchors:
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: content
  type: string
  desc: 备注内容
- name: cc_user_id
  type: string
  desc: 抄送相关人员
- name: ref_tenant_project_approval_flow_comment_approval
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
left: tenant_project_approval.code
right: tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1730
source: l1_code
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
authenticity_note: 备注 ref 存 approval.getCode()。
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

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_file]]

### 字典

- [[dicts/tenant_project_approval_flow_comment__enable]]（`tenant_project_approval_flow_comment.enable`）
