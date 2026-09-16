---
type: table
title: 租户项目审批流程授信表
page_key: tenant_project_approval_flow_credit
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_credit
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批流程授信表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### credit_parties

`credited_cust_id`, `credited_cust_name`, `crediting_cust_id`, `crediting_cust_name`

### credit_limit

`is_group_limit`, `limit_begin_date`, `limit_end_date`, `credit_limit`, `is_recyclable`

### approval

`ref_tenant_project_approval_flow_credit_project_approval`, `ref_tenant_project_approval_flow_credit_project_approval_node`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`finance_email`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_credit
database: lowcode_pplatform
description: 租户项目审批流程授信表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- credited_cust_name
- crediting_cust_name
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
- key: credit_parties
  title: 授信双方
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
- key: credit_limit
  title: 授信额度
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_credit
- key: approval
  title: 审批流程
  confidence: proposed
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
  nullable: true
  cluster: credit_parties
- name: credited_cust_name
  data_type: string
  description: 被授信方（核心企业）
  nullable: true
  cluster: credit_parties
- name: crediting_cust_id
  data_type: string
  description: 授信方（资金方）id
  nullable: true
  cluster: credit_parties
- name: crediting_cust_name
  data_type: string
  description: 授信方（资金方）
  nullable: true
  cluster: credit_parties
- name: is_group_limit
  data_type: string
  description: 是否为集团额度：Y/N
  nullable: true
  cluster: credit_limit
  dictionary: tenant_project_approval_flow_credit_is_group_limit
- name: limit_begin_date
  data_type: temporal
  description: 额度有效期开始
  nullable: true
  cluster: credit_limit
- name: limit_end_date
  data_type: temporal
  description: 额度有效期结束
  nullable: true
  cluster: credit_limit
- name: credit_limit
  data_type: number
  description: 授信额度
  nullable: true
  cluster: credit_limit
- name: is_recyclable
  data_type: string
  description: 额度是否可循环：Y/N
  nullable: true
  cluster: credit_limit
  dictionary: tenant_project_approval_flow_credit_is_recyclable
- name: finance_email
  data_type: string
  description: 资金方邮箱（需格式校验）
  nullable: true
- name: ref_tenant_project_approval_flow_credit_project_approval
  data_type: string
  description: 关联项目审批
  nullable: true
  cluster: approval
- name: ref_tenant_project_approval_flow_credit_project_approval_node
  data_type: string
  description: 关联项目审批流程节点
  nullable: true
  cluster: approval
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: common
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
```
