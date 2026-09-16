---
type: table
title: 企业立项申请表
page_key: wechat_project_approval_apply
belong: tables
status: draft
aliases: []
anchors:
- wechat_project_approval_apply
sources:
- database_schema:lowcode_pplatform.wechat_project_approval_apply
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 企业立项申请表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### approval_flow

`sp_no`, `sp_type`, `sp_pass_time`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `apply_start_time`

### project_core

`project_approval_name`, `main_project_name`, `project_online_name`, `project_id`, `project_config_time`, `project_type`, `project_phase`, `project_exception_remark`, `project_focus_level`

### product

`product_type`, `product_type_arr`

### stakeholders

`bussiness_manager`, `op_contact`, `op_contact_group`, `archives_contact`, `archives_contact_group`, `risk_control_contact`, `risk_control_contact_group`, `project_manager`, `solution_manager`, `solution_manager_wxid`, `old_solution_manager`

### statics

`statics_op_user`, `statics_op_time`

### custom

`custom_field_one`, `custom_field_two`, `custom_field_three`, `custom_field_statistics_one`

### business_meta

`prd`, `organization_id`, `ka_white_label`, `business_center`, `enterprise_full_name`, `data_source`, `system_delivery`

### capital

`first_settlement_time`, `capital_org_full_name`, `capital_branch_name`, `bank_quota`, `core_enterprise`, `credit_enhancer`, `fund_manager`, `lls_participate_role`, `shelf_scale`

### notes

`comment`, `remark`

## 字段

```ground:table
table: wechat_project_approval_apply
database: lowcode_pplatform
description: 企业立项申请表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- project_approval_name
- main_project_name
- project_online_name
- code
- name
- capital_org_full_name
- capital_branch_name
- enterprise_full_name
clusters:
- key: common
  title: 通用审计与标识
  include: always
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: approval_flow
  title: 审批流程（企微审批+流程实例）
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: project_core
  title: 立项项目主信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: product
  title: 产品类型
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: stakeholders
  title: 项目干系人与对接人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: statics
  title: 项目统计更新
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: custom
  title: 自定义扩展字段
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: business_meta
  title: 业务属性与来源
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: capital
  title: 资方与金融要素
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: notes
  title: 备注文本
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: sp_no
  data_type: string
  description: 企微审批编号
  nullable: true
  cluster: approval_flow
- name: sp_type
  data_type: string
  description: 类型
  nullable: true
  cluster: approval_flow
- name: product_type
  data_type: string
  description: 产品类型
  nullable: true
  cluster: product
- name: project_approval_name
  data_type: string
  description: 立项名称
  nullable: true
  cluster: project_core
- name: main_project_name
  data_type: string
  description: 主项目名称
  nullable: true
  cluster: project_core
- name: sp_pass_time
  data_type: temporal
  description: 立项审批通过时间
  nullable: true
  cluster: approval_flow
- name: project_online_name
  data_type: string
  description: 项目上线名称
  nullable: true
  cluster: project_core
- name: prd
  data_type: string
  description: 是否投产
  nullable: true
  cluster: business_meta
  dictionary: wechat_project_approval_apply_prd
- name: bussiness_manager
  data_type: string
  description: 业务经理
  nullable: true
  cluster: stakeholders
- name: op_contact
  data_type: string
  description: 运营对接人
  nullable: true
  cluster: stakeholders
- name: op_contact_group
  data_type: string
  description: 运营组别
  nullable: true
  cluster: stakeholders
- name: archives_contact
  data_type: string
  description: 档案对接人
  nullable: true
  cluster: stakeholders
- name: archives_contact_group
  data_type: string
  description: 档案组别
  nullable: true
  cluster: stakeholders
- name: risk_control_contact
  data_type: string
  description: 风控对接人
  nullable: true
  cluster: stakeholders
- name: risk_control_contact_group
  data_type: string
  description: 风控对接人组别
  nullable: true
  cluster: stakeholders
- name: comment
  data_type: string
  description: 备注
  nullable: true
  cluster: notes
- name: project_manager
  data_type: string
  description: 项目经理
  nullable: true
  cluster: stakeholders
- name: solution_manager
  data_type: string
  description: 方案经理
  nullable: true
  cluster: stakeholders
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
- name: project_id
  data_type: number
  description: 关联的项目id
  nullable: true
  cluster: project_core
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
  dictionary: wechat_project_approval_apply_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: notes
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
  cluster: approval_flow
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
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: business_meta
- name: project_config_time
  data_type: temporal
  description: 项目配置时间
  nullable: true
  cluster: project_core
- name: first_settlement_time
  data_type: temporal
  description: 首笔放款时间
  nullable: true
  cluster: capital
- name: project_type
  data_type: string
  description: 项目类型
  nullable: true
  cluster: project_core
  dictionary: wechat_project_approval_apply_project_type
- name: ka_white_label
  data_type: string
  description: KA是否贴牌
  nullable: true
  cluster: business_meta
  dictionary: wechat_project_approval_apply_ka_white_label
- name: project_phase
  data_type: string
  description: 项目阶段
  nullable: true
  cluster: project_core
  dictionary: wechat_project_approval_apply_project_phase
- name: apply_start_time
  data_type: temporal
  description: 发起立项时间
  nullable: true
  cluster: approval_flow
- name: business_center
  data_type: string
  description: 业务中心
  nullable: true
  cluster: business_meta
- name: capital_org_full_name
  data_type: string
  description: 资方全称
  nullable: true
  cluster: capital
- name: project_exception_remark
  data_type: string
  description: 项目异常备注
  nullable: true
  cluster: project_core
- name: capital_branch_name
  data_type: string
  description: 资方分支行
  nullable: true
  cluster: capital
- name: enterprise_full_name
  data_type: string
  description: 企业全称
  nullable: true
  cluster: business_meta
- name: project_focus_level
  data_type: string
  description: 项目投入关注度
  nullable: true
  cluster: project_core
- name: data_source
  data_type: string
  description: 数据来源
  nullable: true
  cluster: business_meta
  dictionary: wechat_project_approval_apply_data_source
- name: custom_field_statistics_one
  data_type: string
  description: 自定义字段一(统计用)
  nullable: true
  cluster: custom
- name: solution_manager_wxid
  data_type: string
  description: 方案经理企微id
  nullable: true
  cluster: stakeholders
- name: old_solution_manager
  data_type: string
  description: 前方案经理
  nullable: true
  cluster: stakeholders
- name: system_delivery
  data_type: string
  description: 系统交付方式
  nullable: true
  cluster: business_meta
- name: product_type_arr
  data_type: string
  description: 产品类型数组
  nullable: true
  cluster: product
- name: statics_op_user
  data_type: string
  description: 项目统计更新用户
  nullable: true
  cluster: statics
- name: statics_op_time
  data_type: temporal
  description: 项目统计更新时间
  nullable: true
  cluster: statics
- name: bank_quota
  data_type: string
  description: 银行额度(万元)
  nullable: true
  cluster: capital
- name: core_enterprise
  data_type: string
  description: 核心企业
  nullable: true
  cluster: capital
- name: credit_enhancer
  data_type: string
  description: 增信主体
  nullable: true
  cluster: capital
- name: fund_manager
  data_type: string
  description: 管理人
  nullable: true
  cluster: capital
- name: lls_participate_role
  data_type: string
  description: 联易融参与角色
  nullable: true
  cluster: capital
- name: shelf_scale
  data_type: string
  description: 储架规模(万)
  nullable: true
  cluster: capital
```
