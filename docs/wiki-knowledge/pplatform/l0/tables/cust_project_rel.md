---
type: table
title: 客户项目关联表
page_key: cust_project_rel
belong: tables
status: draft
aliases: []
anchors:
- cust_project_rel
sources:
- database_schema:lowcode_pplatform.cust_project_rel
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户项目关联表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### project

`project_id`, `config_model`, `tenant_flg_en`, `project_open_status`

### tenant

`tenant_code`, `app_tenant_code`, `db_tenant_code`

### product_channel

`product_id`, `channel_code`, `ref_cust_project_rel_platform_product`

### relation_profile

`name`, `company_type`, `ref_cust_project_rel_cust_company_info`, `remark`, `organization_id`

### status_flags

`show_flag`, `status`, `top_flag`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### op_contact

`op_contact_a`, `op_contact_b`, `op_contact_a_group`

### verification_contact

`verification_contact`, `verification_contact_group`

### risk_contact

`risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`

### op_update_audit

`op_update_user`, `op_update_time`

## 字段

```ground:table
table: cust_project_rel
database: lowcode_pplatform
description: 客户项目关联表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- channel_code
clusters:
- key: common
  title: 通用
  include: always
- key: project
  title: 项目
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: tenant
  title: 租户
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: product_channel
  title: 产品与渠道
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: relation_profile
  title: 关联信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: status_flags
  title: 关联状态与标记
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: approval
  title: 流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: op_contact
  title: 运营对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: verification_contact
  title: 查验对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: risk_contact
  title: 风控对接
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: op_update_audit
  title: 运营信息更新
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: relation_profile
- name: project_id
  data_type: string
  description: 项目id
  nullable: true
  cluster: project
- name: tenant_code
  data_type: string
  description: 租户
  nullable: true
  cluster: tenant
- name: product_id
  data_type: string
  description: 产品
  nullable: true
  cluster: product_channel
- name: channel_code
  data_type: string
  description: 渠道码
  nullable: true
  cluster: product_channel
- name: company_type
  data_type: string
  description: 客户角色(只取一个)
  nullable: true
  cluster: relation_profile
  dictionary: cust_project_rel_company_type
- name: ref_cust_project_rel_cust_company_info
  data_type: string
  description: 客户和项目关系
  nullable: true
  cluster: relation_profile
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_project_rel_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: relation_profile
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
  nullable: true
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
  description: ''
  nullable: true
  cluster: relation_profile
- name: show_flag
  data_type: string
  description: 展示标记
  nullable: true
  cluster: status_flags
  dictionary: cust_project_rel_show_flag
- name: config_model
  data_type: string
  description: 项目配置模式
  nullable: true
  cluster: project
- name: status
  data_type: string
  description: 关联状态
  nullable: true
  cluster: status_flags
  dictionary: cust_project_rel_status
- name: ref_cust_project_rel_platform_product
  data_type: string
  description: 平台产品
  nullable: true
  cluster: product_channel
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  nullable: true
  cluster: project
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
  cluster: verification_contact
- name: verification_contact_group
  data_type: string
  description: 查验组别
  nullable: true
  cluster: verification_contact
- name: risk_control_contact_a
  data_type: string
  description: 风控对接人A
  nullable: true
  cluster: risk_contact
- name: risk_control_contact_b
  data_type: string
  description: 风控对接人B
  nullable: true
  cluster: risk_contact
- name: risk_control_contact_a_group
  data_type: string
  description: 风控组别
  nullable: true
  cluster: risk_contact
- name: top_flag
  data_type: string
  description: 置顶标识
  nullable: true
  cluster: status_flags
  dictionary: cust_project_rel_top_flag
- name: op_update_user
  data_type: string
  description: 运营信息更新人
  nullable: true
  cluster: op_update_audit
- name: op_update_time
  data_type: temporal
  description: 运营信息更新时间
  nullable: true
  cluster: op_update_audit
- name: project_open_status
  data_type: string
  description: 项目开通状态
  nullable: true
  cluster: project
  dictionary: cust_project_rel_project_open_status
```
