---
type: table
title: 微企链项目企业关联运营
page_key: wec_project_cust_operation_rel
belong: tables
status: draft
aliases: []
anchors:
- wec_project_cust_operation_rel
sources:
- database_schema:lowcode_pplatform.wec_project_cust_operation_rel
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 微企链项目企业关联运营

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### company

`company_id`, `company_type`

### op_contact

`op_contact_a`, `op_contact_b`, `op_contact_a_group`

### verification

`verification_contact`, `verification_contact_group`

### risk

`risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### business_identity

`wec_rel_id`, `project_id`, `name`, `organization_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`top_flag`

## 字段

```ground:table
table: wec_project_cust_operation_rel
database: lowcode_pplatform
description: 微企链项目企业关联运营
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: company
  title: 微企链企业
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: op_contact
  title: 运营对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: verification
  title: 查验对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: risk
  title: 风控对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: business_identity
  title: 业务标识与名称
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: wec_rel_id
  data_type: string
  description: 微企链关联关系id
  nullable: true
  cluster: business_identity
- name: company_id
  data_type: string
  description: 微企链企业id
  nullable: true
  cluster: company
- name: company_type
  data_type: string
  description: 微企链企业角色
  nullable: true
  cluster: company
  dictionary: wec_project_cust_operation_rel_company_type
- name: project_id
  data_type: string
  description: 微企链项目id
  nullable: true
  cluster: business_identity
- name: op_contact_a
  data_type: string
  description: 运营对接人A
  nullable: true
  cluster: op_contact
- name: op_contact_b
  data_type: string
  description: 运营对接人B
  nullable: true
  cluster: op_contact
- name: op_contact_a_group
  data_type: string
  description: 运营组别
  nullable: true
  cluster: op_contact
- name: verification_contact
  data_type: string
  description: 查验对接人
  nullable: true
  cluster: verification
- name: verification_contact_group
  data_type: string
  description: 查验组别
  nullable: true
  cluster: verification
- name: risk_control_contact_a
  data_type: string
  description: 风控对接人A
  nullable: true
  cluster: risk
- name: risk_control_contact_b
  data_type: string
  description: 风控对接人B
  nullable: true
  cluster: risk
- name: risk_control_contact_a_group
  data_type: string
  description: 风控组别
  nullable: true
  cluster: risk
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: business_identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: wec_project_cust_operation_rel_enable
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
  cluster: workflow
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
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: business_identity
- name: top_flag
  data_type: string
  description: 置顶标识
  nullable: true
  dictionary: wec_project_cust_operation_rel_top_flag
```
