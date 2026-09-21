---
type: table
title: 微企链项目企业关联运营
page_key: wec_project_cust_operation_rel
belong: tables
status: draft
anchors: [wec_project_cust_operation_rel]
sources: ['database_schema:lowcode_pplatform.wec_project_cust_operation_rel']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wec_project_cust_operation_rel__company_type, wec_project_cust_operation_rel__op_contact_a,
  wec_project_cust_operation_rel__verification_contact, wec_project_cust_operation_rel__risk_control_contact_a,
  wec_project_cust_operation_rel__enable, wec_project_cust_operation_rel__top_flag]
---

# 微企链项目企业关联运营

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: wec_project_cust_operation_rel
database: lowcode_pplatform
desc: 微企链项目企业关联运营
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: wec_rel_id
  type: string
  desc: 微企链关联关系id
- name: company_id
  type: string
  desc: 微企链企业id
- name: company_type
  type: string
  desc: 微企链企业角色
  dict: [ce, cpt]
- name: project_id
  type: string
  desc: 微企链项目id
- name: op_contact_a
  type: string
  desc: 运营对接人A
  dict: ['420', '267', '321', '293', '411', '271', '97', '454']
- name: op_contact_b
  type: string
  desc: 运营对接人B
- name: op_contact_a_group
  type: string
  desc: 运营组别
- name: verification_contact
  type: string
  desc: 查验对接人
  dict: ['454', '305', '321', '141']
- name: verification_contact_group
  type: string
  desc: 查验组别
- name: risk_control_contact_a
  type: string
  desc: 风控对接人A
  dict: ['454', '271', '321', '105', '108']
- name: risk_control_contact_b
  type: string
  desc: 风控对接人B
- name: risk_control_contact_a_group
  type: string
  desc: 风控组别
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict: [Y]
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
- name: top_flag
  type: string
  desc: 置顶标识
  dict: ['0']
```

## 页面链接

### 字典

- [[dicts/wec_project_cust_operation_rel__company_type]]（`wec_project_cust_operation_rel.company_type`）
- [[dicts/wec_project_cust_operation_rel__op_contact_a]]（`wec_project_cust_operation_rel.op_contact_a`）
- [[dicts/wec_project_cust_operation_rel__verification_contact]]（`wec_project_cust_operation_rel.verification_contact`）
- [[dicts/wec_project_cust_operation_rel__risk_control_contact_a]]（`wec_project_cust_operation_rel.risk_control_contact_a`）
- [[dicts/wec_project_cust_operation_rel__enable]]（`wec_project_cust_operation_rel.enable`）
- [[dicts/wec_project_cust_operation_rel__top_flag]]（`wec_project_cust_operation_rel.top_flag`）
