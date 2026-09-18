---
type: table
title: 租户项目审批流程授信表
page_key: tenant_project_approval_flow_credit
belong: tables
status: draft
anchors: [tenant_project_approval_flow_credit]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_flow_credit']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_project_approval_flow_node, tenant_project_approval_flow_credit__is_group_limit,
  tenant_project_approval_flow_credit__is_recyclable, tenant_project_approval_flow_credit__enable,
  tenant_project_approval_flow_credit__app_tenant_code, tenant_project_approval_flow_credit__db_tenant_code]
---

# 租户项目审批流程授信表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### credit_party

`credited_cust_id`, `credited_cust_name`, `crediting_cust_id`, `crediting_cust_name`

### credit_limit

`is_group_limit`, `limit_begin_date`, `limit_end_date`, `credit_limit`, `is_recyclable`

### approval_link

`ref_tenant_project_approval_flow_credit_project_approval`, `ref_tenant_project_approval_flow_credit_project_approval_node`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### org_tenant

`app_tenant_code`, `db_tenant_code`, `organization_id`

### 未归簇

`finance_email`

## 字段

```ground:table
table: tenant_project_approval_flow_credit
database: lowcode_pplatform
description: 租户项目审批流程授信表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [credited_cust_name, crediting_cust_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: credit_party
  title: 授信主体
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
- key: credit_limit
  title: 额度设置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
- key: approval_link
  title: 审批关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
- key: org_tenant
  title: 组织租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: credited_cust_id
  data_type: string
  description: 被授信方（核心企业）id
  cluster: credit_party
- name: credited_cust_name
  data_type: string
  description: 被授信方（核心企业）
  cluster: credit_party
- name: crediting_cust_id
  data_type: string
  description: 授信方（资金方）id
  cluster: credit_party
- name: crediting_cust_name
  data_type: string
  description: 授信方（资金方）
  cluster: credit_party
- name: is_group_limit
  data_type: string
  description: 是否为集团额度：Y/N
  cluster: credit_limit
  dictionary: tenant_project_approval_flow_credit__is_group_limit
- name: limit_begin_date
  data_type: temporal
  description: 额度有效期开始
  cluster: credit_limit
- name: limit_end_date
  data_type: temporal
  description: 额度有效期结束
  cluster: credit_limit
- name: credit_limit
  data_type: number
  description: 授信额度
  cluster: credit_limit
- name: is_recyclable
  data_type: string
  description: 额度是否可循环：Y/N
  cluster: credit_limit
  dictionary: tenant_project_approval_flow_credit__is_recyclable
- name: finance_email
  data_type: string
  description: 资金方邮箱（需格式校验）
- name: ref_tenant_project_approval_flow_credit_project_approval
  data_type: string
  description: 关联项目审批
  cluster: approval_link
- name: ref_tenant_project_approval_flow_credit_project_approval_node
  data_type: string
  description: 关联项目审批流程节点
  cluster: approval_link
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
  dictionary: tenant_project_approval_flow_credit__enable
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
  cluster: approval_link
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: org_tenant
  dictionary: tenant_project_approval_flow_credit__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: org_tenant
  dictionary: tenant_project_approval_flow_credit__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval_link
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval_link
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval_link
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: org_tenant
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
overlap:
  probed: true
  ratio: 1.0
  sample_size: 141
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 名称证据无直接匹配，但本表注释为关联项目审批，且 overlap ratio=1.0、sample_size=141、miss=0，判
  likely。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.code
right: tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval_node
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval_node
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
overlap:
  probed: true
  ratio: 1.0
  sample_size: 154
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 名称证据无直接匹配，但本表注释为关联项目审批流程节点，且 overlap ratio=1.0、sample_size=154、miss=0，判
  likely。
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_node]]

### 字典

- [[dicts/tenant_project_approval_flow_credit__is_group_limit]]（`tenant_project_approval_flow_credit.is_group_limit`）
- [[dicts/tenant_project_approval_flow_credit__is_recyclable]]（`tenant_project_approval_flow_credit.is_recyclable`）
- [[dicts/tenant_project_approval_flow_credit__enable]]（`tenant_project_approval_flow_credit.enable`）
- [[dicts/tenant_project_approval_flow_credit__app_tenant_code]]（`tenant_project_approval_flow_credit.app_tenant_code`）
- [[dicts/tenant_project_approval_flow_credit__db_tenant_code]]（`tenant_project_approval_flow_credit.db_tenant_code`）
