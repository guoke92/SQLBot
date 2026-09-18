---
type: table
title: 微企链项目关联运营
page_key: wec_project_operation_rel
belong: tables
status: draft
anchors: [wec_project_operation_rel]
sources: ['database_schema:lowcode_pplatform.wec_project_operation_rel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wec_project_operation_rel__op_contact_a, wec_project_operation_rel__op_contact_a_group,
  wec_project_operation_rel__verification_contact, wec_project_operation_rel__risk_control_contact_a,
  wec_project_operation_rel__risk_control_contact_a_group, wec_project_operation_rel__custom_field_one,
  wec_project_operation_rel__custom_field_two, wec_project_operation_rel__project_tag,
  wec_project_operation_rel__enable, wec_project_operation_rel__app_tenant_code, wec_project_operation_rel__top_flag]
---

# 微企链项目关联运营

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`, `text`

### project

`wec_project_id`, `first_settlement_time`, `project_tag`, `project_relation`, `bussiness_project_relation`, `organization_id`, `top_flag`

### approval

`wechat_audit_no`, `wechat_audit_pass_time`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### operation_contact

`op_contact_a`, `op_contact_b`, `op_contact_a_group`

### verification

`verification_contact`, `verification_contact_group`

### risk_control

`risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`

### roles

`solution_manager`, `business_manager`, `business_group`

### custom

`custom_field_one`, `custom_field_two`, `custom_field_three`

## 字段

```ground:table
table: wec_project_operation_rel
database: lowcode_pplatform
description: 微企链项目关联运营
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: project
  title: 微企链项目
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: operation_contact
  title: 运营对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: verification
  title: 查验对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: risk_control
  title: 风控对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: roles
  title: 业务角色
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_operation_rel
- key: custom
  title: 自定义字段
  trust: proposed
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
  cluster: project
- name: wechat_audit_no
  data_type: string
  description: 企微审批编号
  cluster: approval
- name: wechat_audit_pass_time
  data_type: temporal
  description: 项目立项审批通过时间
  cluster: approval
- name: op_contact_a
  data_type: string
  description: 运营对接人A
  cluster: operation_contact
  dictionary: wec_project_operation_rel__op_contact_a
- name: op_contact_b
  data_type: string
  description: 运营对接人B
  cluster: operation_contact
- name: op_contact_a_group
  data_type: string
  description: 运营组别
  cluster: operation_contact
  dictionary: wec_project_operation_rel__op_contact_a_group
- name: verification_contact
  data_type: string
  description: 查验对接人
  cluster: verification
  dictionary: wec_project_operation_rel__verification_contact
- name: verification_contact_group
  data_type: string
  description: 查验组别
  cluster: verification
- name: risk_control_contact_a
  data_type: string
  description: 风控对接人A
  cluster: risk_control
  dictionary: wec_project_operation_rel__risk_control_contact_a
- name: risk_control_contact_b
  data_type: string
  description: 风控对接人B
  cluster: risk_control
- name: risk_control_contact_a_group
  data_type: string
  description: 风控组别
  cluster: risk_control
  dictionary: wec_project_operation_rel__risk_control_contact_a_group
- name: solution_manager
  data_type: string
  description: 方案经理
  cluster: roles
- name: business_manager
  data_type: string
  description: 业务经理
  cluster: roles
- name: business_group
  data_type: string
  description: 关联业务部门
  cluster: roles
- name: first_settlement_time
  data_type: temporal
  description: 首笔落地时间
  cluster: project
- name: custom_field_one
  data_type: string
  description: 自定义字段一
  cluster: custom
  dictionary: wec_project_operation_rel__custom_field_one
- name: custom_field_two
  data_type: string
  description: 自定义字段二
  cluster: custom
  dictionary: wec_project_operation_rel__custom_field_two
- name: custom_field_three
  data_type: string
  description: 自定义字段三
  cluster: custom
- name: project_tag
  data_type: string
  description: 项目标签
  cluster: project
  dictionary: wec_project_operation_rel__project_tag
- name: project_relation
  data_type: string
  description: 项目归属
  cluster: project
- name: bussiness_project_relation
  data_type: string
  description: 运营项目归属
  cluster: project
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
  dictionary: wec_project_operation_rel__enable
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
  dictionary: wec_project_operation_rel__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: project
- name: top_flag
  data_type: string
  description: 置顶标识
  cluster: project
  dictionary: wec_project_operation_rel__top_flag
- name: text
  data_type: string
  cluster: common
```

## 页面链接

### 字典

- [[dicts/wec_project_operation_rel__op_contact_a]]（`wec_project_operation_rel.op_contact_a`）
- [[dicts/wec_project_operation_rel__op_contact_a_group]]（`wec_project_operation_rel.op_contact_a_group`）
- [[dicts/wec_project_operation_rel__verification_contact]]（`wec_project_operation_rel.verification_contact`）
- [[dicts/wec_project_operation_rel__risk_control_contact_a]]（`wec_project_operation_rel.risk_control_contact_a`）
- [[dicts/wec_project_operation_rel__risk_control_contact_a_group]]（`wec_project_operation_rel.risk_control_contact_a_group`）
- [[dicts/wec_project_operation_rel__custom_field_one]]（`wec_project_operation_rel.custom_field_one`）
- [[dicts/wec_project_operation_rel__custom_field_two]]（`wec_project_operation_rel.custom_field_two`）
- [[dicts/wec_project_operation_rel__project_tag]]（`wec_project_operation_rel.project_tag`）
- [[dicts/wec_project_operation_rel__enable]]（`wec_project_operation_rel.enable`）
- [[dicts/wec_project_operation_rel__app_tenant_code]]（`wec_project_operation_rel.app_tenant_code`）
- [[dicts/wec_project_operation_rel__top_flag]]（`wec_project_operation_rel.top_flag`）
