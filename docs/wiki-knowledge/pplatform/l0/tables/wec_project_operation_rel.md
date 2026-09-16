---
type: table
title: 微企链项目关联运营
page_key: wec_project_operation_rel
belong: tables
status: draft
aliases: []
anchors:
- wec_project_operation_rel
sources:
- database_schema:lowcode_pplatform.wec_project_operation_rel
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 微企链项目关联运营

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### project

`wec_project_id`, `project_tag`, `project_relation`, `bussiness_project_relation`, `top_flag`

### wechat_audit

`wechat_audit_no`, `wechat_audit_pass_time`

### operation_contact

`op_contact_a`, `op_contact_b`, `op_contact_a_group`

### verification

`verification_contact`, `verification_contact_group`

### risk_control

`risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`

### business

`solution_manager`, `business_manager`, `business_group`

### custom

`custom_field_one`, `custom_field_two`, `custom_field_three`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### text_misc

`name`, `remark`, `text`

### 未归簇

`first_settlement_time`, `organization_id`

## 字段

```ground:table
table: wec_project_operation_rel
database: lowcode_pplatform
description: 微企链项目关联运营
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
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: project
  title: 项目归属与标签
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: wechat_audit
  title: 企微审批
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: operation_contact
  title: 运营对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: verification
  title: 查验对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: risk_control
  title: 风控对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: business
  title: 业务方案
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: custom
  title: 自定义字段
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: text_misc
  title: 名称与备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: wec_project_id
  data_type: string
  description: 微企链项目id
  nullable: true
  cluster: project
- name: wechat_audit_no
  data_type: string
  description: 企微审批编号
  nullable: true
  cluster: wechat_audit
- name: wechat_audit_pass_time
  data_type: temporal
  description: 项目立项审批通过时间
  nullable: true
  cluster: wechat_audit
- name: op_contact_a
  data_type: string
  description: 运营对接人A
  nullable: true
  cluster: operation_contact
- name: op_contact_b
  data_type: string
  description: 运营对接人B
  nullable: true
  cluster: operation_contact
- name: op_contact_a_group
  data_type: string
  description: 运营组别
  nullable: true
  cluster: operation_contact
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
  cluster: risk_control
- name: risk_control_contact_b
  data_type: string
  description: 风控对接人B
  nullable: true
  cluster: risk_control
- name: risk_control_contact_a_group
  data_type: string
  description: 风控组别
  nullable: true
  cluster: risk_control
- name: solution_manager
  data_type: string
  description: 方案经理
  nullable: true
  cluster: business
- name: business_manager
  data_type: string
  description: 业务经理
  nullable: true
  cluster: business
- name: business_group
  data_type: string
  description: 关联业务部门
  nullable: true
  cluster: business
- name: first_settlement_time
  data_type: temporal
  description: 首笔落地时间
  nullable: true
- name: custom_field_one
  data_type: string
  description: 自定义字段一
  nullable: true
  cluster: custom
- name: custom_field_two
  data_type: string
  description: 自定义字段二
  nullable: true
  cluster: custom
- name: custom_field_three
  data_type: string
  description: 自定义字段三
  nullable: true
  cluster: custom
- name: project_tag
  data_type: string
  description: 项目标签
  nullable: true
  cluster: project
  dictionary: wec_project_operation_rel_project_tag
- name: project_relation
  data_type: string
  description: 项目归属
  nullable: true
  cluster: project
- name: bussiness_project_relation
  data_type: string
  description: 运营项目归属
  nullable: true
  cluster: project
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: text_misc
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: wec_project_operation_rel_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: text_misc
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
- name: top_flag
  data_type: string
  description: 置顶标识
  nullable: true
  cluster: project
  dictionary: wec_project_operation_rel_top_flag
- name: text
  data_type: string
  description: ''
  nullable: true
  cluster: text_misc
```
