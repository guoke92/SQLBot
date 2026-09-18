---
type: table
title: 微企链项目企业关联运营
page_key: wec_project_cust_operation_rel
belong: tables
status: draft
anchors: [wec_project_cust_operation_rel]
sources: ['database_schema:lowcode_pplatform.wec_project_cust_operation_rel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wec_project_cust_operation_rel__company_type, wec_project_cust_operation_rel__op_contact_a,
  wec_project_cust_operation_rel__verification_contact, wec_project_cust_operation_rel__risk_control_contact_a,
  wec_project_cust_operation_rel__enable, wec_project_cust_operation_rel__app_tenant_code,
  wec_project_cust_operation_rel__top_flag]
---

# 微企链项目企业关联运营

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`, `top_flag`

### wec_identity

`wec_rel_id`, `company_id`, `company_type`, `project_id`, `organization_id`

### op_contact

`op_contact_a`, `op_contact_b`, `op_contact_a_group`

### verification

`verification_contact`, `verification_contact_group`

### risk_control

`risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: wec_project_cust_operation_rel
database: lowcode_pplatform
description: 微企链项目企业关联运营
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: wec_identity
  title: 微企链关联主体
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: op_contact
  title: 运营对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: verification
  title: 查验对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: risk_control
  title: 风控对接
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wec_project_cust_operation_rel
- key: act_procinst
  title: 流程审批
  trust: proposed
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
  cluster: wec_identity
- name: company_id
  data_type: string
  description: 微企链企业id
  cluster: wec_identity
- name: company_type
  data_type: string
  description: 微企链企业角色
  cluster: wec_identity
  dictionary: wec_project_cust_operation_rel__company_type
- name: project_id
  data_type: string
  description: 微企链项目id
  cluster: wec_identity
- name: op_contact_a
  data_type: string
  description: 运营对接人A
  cluster: op_contact
  dictionary: wec_project_cust_operation_rel__op_contact_a
- name: op_contact_b
  data_type: string
  description: 运营对接人B
  cluster: op_contact
- name: op_contact_a_group
  data_type: string
  description: 运营组别
  cluster: op_contact
- name: verification_contact
  data_type: string
  description: 查验对接人
  cluster: verification
  dictionary: wec_project_cust_operation_rel__verification_contact
- name: verification_contact_group
  data_type: string
  description: 查验组别
  cluster: verification
- name: risk_control_contact_a
  data_type: string
  description: 风控对接人A
  cluster: risk_control
  dictionary: wec_project_cust_operation_rel__risk_control_contact_a
- name: risk_control_contact_b
  data_type: string
  description: 风控对接人B
  cluster: risk_control
- name: risk_control_contact_a_group
  data_type: string
  description: 风控组别
  cluster: risk_control
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
  dictionary: wec_project_cust_operation_rel__enable
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
  cluster: common
  dictionary: wec_project_cust_operation_rel__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
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
  cluster: wec_identity
- name: top_flag
  data_type: string
  description: 置顶标识
  cluster: common
  dictionary: wec_project_cust_operation_rel__top_flag
```

## 页面链接

### 字典

- [[dicts/wec_project_cust_operation_rel__company_type]]（`wec_project_cust_operation_rel.company_type`）
- [[dicts/wec_project_cust_operation_rel__op_contact_a]]（`wec_project_cust_operation_rel.op_contact_a`）
- [[dicts/wec_project_cust_operation_rel__verification_contact]]（`wec_project_cust_operation_rel.verification_contact`）
- [[dicts/wec_project_cust_operation_rel__risk_control_contact_a]]（`wec_project_cust_operation_rel.risk_control_contact_a`）
- [[dicts/wec_project_cust_operation_rel__enable]]（`wec_project_cust_operation_rel.enable`）
- [[dicts/wec_project_cust_operation_rel__app_tenant_code]]（`wec_project_cust_operation_rel.app_tenant_code`）
- [[dicts/wec_project_cust_operation_rel__top_flag]]（`wec_project_cust_operation_rel.top_flag`）
