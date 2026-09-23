---
type: table
title: 租户项目审批流程授信表
page_key: tenant_project_approval_flow_credit
belong: tables
status: draft
anchors:
- tenant_project_approval_flow_credit
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- tenant_project_approval
- tenant_project_approval_flow_node
- tenant_project_approval_flow_credit__is_group_limit
- tenant_project_approval_flow_credit__is_recyclable
- tenant_project_approval_flow_credit__enable
---
# 租户项目审批流程授信表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_flow_credit
database: lowcode_pplatform
desc: 租户项目审批流程授信表
inactive: false
primary_key:
- id
grain: 审批单授信行
name_anchors:
- credited_cust_name
- crediting_cust_name
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: credited_cust_id
  type: string
  desc: 被授信方（核心企业）id
- name: credited_cust_name
  type: string
  desc: 被授信方（核心企业）
- name: crediting_cust_id
  type: string
  desc: 授信方（资金方）id
- name: crediting_cust_name
  type: string
  desc: 授信方（资金方）
- name: is_group_limit
  type: string
  desc: 是否为集团额度：Y/N
  dict:
  - Y
  - N
  label: [是, 否]
- name: limit_begin_date
  type: temporal
  desc: 额度有效期开始
- name: limit_end_date
  type: temporal
  desc: 额度有效期结束
- name: credit_limit
  type: number
  desc: 授信额度
- name: is_recyclable
  type: string
  desc: 额度是否可循环：Y/N
  dict:
  - Y
  - N
  label: [是, 否]
- name: finance_email
  type: string
  desc: 资金方邮箱（需格式校验）
- name: ref_tenant_project_approval_flow_credit_project_approval
  type: string
  desc: 关联项目审批
- name: ref_tenant_project_approval_flow_credit_project_approval_node
  type: string
  desc: 关联项目审批流程节点
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
right: tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1551
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_credit_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 141
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 授信按审批 code。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.code
right: tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval_node
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalDeskApplication.java:634
source: l1_code
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_credit_project_approval_node
  comment: 关联项目审批流程节点
overlap:
  probed: true
  ratio: 1.0
  sample_size: 154
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 额度节点 ref 存 node.getCode()。
```
## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_node]]

### 概念

- [[concepts/approval_credit_not_quota]]

### 字典

- [[dicts/tenant_project_approval_flow_credit__is_group_limit]]（`tenant_project_approval_flow_credit.is_group_limit`）
- [[dicts/tenant_project_approval_flow_credit__is_recyclable]]（`tenant_project_approval_flow_credit.is_recyclable`）
- [[dicts/tenant_project_approval_flow_credit__enable]]（`tenant_project_approval_flow_credit.enable`）
