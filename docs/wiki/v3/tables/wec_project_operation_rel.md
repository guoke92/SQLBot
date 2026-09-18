---
type: table
title: 微企链项目关联运营
page_key: wec_project_operation_rel
belong: tables
status: draft
anchors: [wec_project_operation_rel]
sources: ['database_schema:lowcode_pplatform.wec_project_operation_rel']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wec_project_operation_rel__project_tag, wec_project_operation_rel__enable,
  wec_project_operation_rel__top_flag]
---

# 微企链项目关联运营

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: wec_project_operation_rel
database: lowcode_pplatform
desc: 微企链项目关联运营
inactive: false
primary_key: [id]
grain: 企微项目与运营联系人
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: wec_project_id
  type: string
  desc: 微企链项目id
- name: wechat_audit_no
  type: string
  desc: 企微审批编号
- name: wechat_audit_pass_time
  type: temporal
  desc: 项目立项审批通过时间
- name: op_contact_a
  type: string
  desc: 运营对接人A
- name: op_contact_b
  type: string
  desc: 运营对接人B
- name: op_contact_a_group
  type: string
  desc: 运营组别
- name: verification_contact
  type: string
  desc: 查验对接人
- name: verification_contact_group
  type: string
  desc: 查验组别
- name: risk_control_contact_a
  type: string
  desc: 风控对接人A
- name: risk_control_contact_b
  type: string
  desc: 风控对接人B
- name: risk_control_contact_a_group
  type: string
  desc: 风控组别
- name: solution_manager
  type: string
  desc: 方案经理
- name: business_manager
  type: string
  desc: 业务经理
- name: business_group
  type: string
  desc: 关联业务部门
- name: first_settlement_time
  type: temporal
  desc: 首笔落地时间
- name: custom_field_one
  type: string
  desc: 自定义字段一
- name: custom_field_two
  type: string
  desc: 自定义字段二
- name: custom_field_three
  type: string
  desc: 自定义字段三
- name: project_tag
  type: string
  desc: 项目标签
  dict: [TEST, PRD]
- name: project_relation
  type: string
  desc: 项目归属
- name: bussiness_project_relation
  type: string
  desc: 运营项目归属
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
- name: text
  type: string
```

## 页面链接

### 字典

- [[dicts/wec_project_operation_rel__project_tag]]（`wec_project_operation_rel.project_tag`）
- [[dicts/wec_project_operation_rel__enable]]（`wec_project_operation_rel.enable`）
- [[dicts/wec_project_operation_rel__top_flag]]（`wec_project_operation_rel.top_flag`）
