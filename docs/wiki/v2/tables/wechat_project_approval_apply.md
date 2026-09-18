---
type: table
title: 企业立项申请表
page_key: wechat_project_approval_apply
belong: tables
status: draft
anchors: [wechat_project_approval_apply]
sources: ['database_schema:lowcode_pplatform.wechat_project_approval_apply']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wechat_project_approval_field_history, wechat_project_approval_apply__sp_type,
  wechat_project_approval_apply__product_type, wechat_project_approval_apply__prd,
  wechat_project_approval_apply__enable, wechat_project_approval_apply__act_procinst_status,
  wechat_project_approval_apply__project_type, wechat_project_approval_apply__ka_white_label,
  wechat_project_approval_apply__project_phase, wechat_project_approval_apply__data_source,
  wechat_project_approval_apply__system_delivery, wechat_project_approval_apply__lls_participate_role]
---

# 企业立项申请表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `comment`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### approval

`sp_no`, `sp_type`, `sp_pass_time`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `apply_start_time`, `data_source`

### project

`project_approval_name`, `main_project_name`, `project_online_name`, `prd`, `project_id`, `project_config_time`, `project_type`, `ka_white_label`, `project_phase`, `project_exception_remark`, `project_focus_level`, `system_delivery`

### product

`product_type`, `product_type_arr`

### contacts

`bussiness_manager`, `op_contact`, `op_contact_group`, `archives_contact`, `archives_contact_group`, `risk_control_contact`, `risk_control_contact_group`, `project_manager`, `solution_manager`, `solution_manager_wxid`, `old_solution_manager`

### custom

`custom_field_one`, `custom_field_two`, `custom_field_three`, `custom_field_statistics_one`

### statics

`statics_op_user`, `statics_op_time`

### capital

`first_settlement_time`, `capital_org_full_name`, `capital_branch_name`, `bank_quota`, `core_enterprise`, `credit_enhancer`, `fund_manager`, `lls_participate_role`, `shelf_scale`

### org

`organization_id`, `business_center`, `enterprise_full_name`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: wechat_project_approval_apply
database: lowcode_pplatform
description: 企业立项申请表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [project_approval_name, main_project_name, project_online_name, code,
  name, capital_org_full_name, capital_branch_name, enterprise_full_name]
clusters:
- key: common
  title: 通用
  include: always
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: project
  title: 立项项目
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: product
  title: 产品
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: contacts
  title: 对接人与角色
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: custom
  title: 自定义字段
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: statics
  title: 统计
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: capital
  title: 资方与融资要素
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: org
  title: 组织与主体
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_apply
- key: tenant
  title: 租户标识
  trust: proposed
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
  cluster: approval
- name: sp_type
  data_type: string
  description: 类型
  cluster: approval
  dictionary: wechat_project_approval_apply__sp_type
- name: product_type
  data_type: string
  description: 产品类型
  cluster: product
  dictionary: wechat_project_approval_apply__product_type
- name: project_approval_name
  data_type: string
  description: 立项名称
  cluster: project
- name: main_project_name
  data_type: string
  description: 主项目名称
  cluster: project
- name: sp_pass_time
  data_type: temporal
  description: 立项审批通过时间
  cluster: approval
- name: project_online_name
  data_type: string
  description: 项目上线名称
  cluster: project
- name: prd
  data_type: string
  description: 是否投产
  cluster: project
  dictionary: wechat_project_approval_apply__prd
- name: bussiness_manager
  data_type: string
  description: 业务经理
  cluster: contacts
- name: op_contact
  data_type: string
  description: 运营对接人
  cluster: contacts
- name: op_contact_group
  data_type: string
  description: 运营组别
  cluster: contacts
- name: archives_contact
  data_type: string
  description: 档案对接人
  cluster: contacts
- name: archives_contact_group
  data_type: string
  description: 档案组别
  cluster: contacts
- name: risk_control_contact
  data_type: string
  description: 风控对接人
  cluster: contacts
- name: risk_control_contact_group
  data_type: string
  description: 风控对接人组别
  cluster: contacts
- name: comment
  data_type: string
  description: 备注
  cluster: common
- name: project_manager
  data_type: string
  description: 项目经理
  cluster: contacts
- name: solution_manager
  data_type: string
  description: 方案经理
  cluster: contacts
- name: custom_field_one
  data_type: string
  description: 自定义字段一
  cluster: custom
- name: custom_field_two
  data_type: string
  description: 自定义字段二
  cluster: custom
- name: custom_field_three
  data_type: string
  description: 自定义字段三
  cluster: custom
- name: project_id
  data_type: number
  description: 关联的项目id
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
  dictionary: wechat_project_approval_apply__enable
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
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
  dictionary: wechat_project_approval_apply__act_procinst_status
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: org
- name: project_config_time
  data_type: temporal
  description: 项目配置时间
  cluster: project
- name: first_settlement_time
  data_type: temporal
  description: 首笔放款时间
  cluster: capital
- name: project_type
  data_type: string
  description: 项目类型
  cluster: project
  dictionary: wechat_project_approval_apply__project_type
- name: ka_white_label
  data_type: string
  description: KA是否贴牌
  cluster: project
  dictionary: wechat_project_approval_apply__ka_white_label
- name: project_phase
  data_type: string
  description: 项目阶段
  cluster: project
  dictionary: wechat_project_approval_apply__project_phase
- name: apply_start_time
  data_type: temporal
  description: 发起立项时间
  cluster: approval
- name: business_center
  data_type: string
  description: 业务中心
  cluster: org
- name: capital_org_full_name
  data_type: string
  description: 资方全称
  cluster: capital
- name: project_exception_remark
  data_type: string
  description: 项目异常备注
  cluster: project
- name: capital_branch_name
  data_type: string
  description: 资方分支行
  cluster: capital
- name: enterprise_full_name
  data_type: string
  description: 企业全称
  cluster: org
- name: project_focus_level
  data_type: string
  description: 项目投入关注度
  cluster: project
- name: data_source
  data_type: string
  description: 数据来源
  cluster: approval
  dictionary: wechat_project_approval_apply__data_source
- name: custom_field_statistics_one
  data_type: string
  description: 自定义字段一(统计用)
  cluster: custom
- name: solution_manager_wxid
  data_type: string
  description: 方案经理企微id
  cluster: contacts
- name: old_solution_manager
  data_type: string
  description: 前方案经理
  cluster: contacts
- name: system_delivery
  data_type: string
  description: 系统交付方式
  cluster: project
  dictionary: wechat_project_approval_apply__system_delivery
- name: product_type_arr
  data_type: string
  description: 产品类型数组
  cluster: product
- name: statics_op_user
  data_type: string
  description: 项目统计更新用户
  cluster: statics
- name: statics_op_time
  data_type: temporal
  description: 项目统计更新时间
  cluster: statics
- name: bank_quota
  data_type: string
  description: 银行额度(万元)
  cluster: capital
- name: core_enterprise
  data_type: string
  description: 核心企业
  cluster: capital
- name: credit_enhancer
  data_type: string
  description: 增信主体
  cluster: capital
- name: fund_manager
  data_type: string
  description: 管理人
  cluster: capital
- name: lls_participate_role
  data_type: string
  description: 联易融参与角色
  cluster: capital
  dictionary: wechat_project_approval_apply__lls_participate_role
- name: shelf_scale
  data_type: string
  description: 储架规模(万)
  cluster: capital
```

## 页面链接

### 关联表

- [[tables/wechat_project_approval_field_history]]

### 字典

- [[dicts/wechat_project_approval_apply__sp_type]]（`wechat_project_approval_apply.sp_type`）
- [[dicts/wechat_project_approval_apply__product_type]]（`wechat_project_approval_apply.product_type`）
- [[dicts/wechat_project_approval_apply__prd]]（`wechat_project_approval_apply.prd`）
- [[dicts/wechat_project_approval_apply__enable]]（`wechat_project_approval_apply.enable`）
- [[dicts/wechat_project_approval_apply__act_procinst_status]]（`wechat_project_approval_apply.act_procinst_status`）
- [[dicts/wechat_project_approval_apply__project_type]]（`wechat_project_approval_apply.project_type`）
- [[dicts/wechat_project_approval_apply__ka_white_label]]（`wechat_project_approval_apply.ka_white_label`）
- [[dicts/wechat_project_approval_apply__project_phase]]（`wechat_project_approval_apply.project_phase`）
- [[dicts/wechat_project_approval_apply__data_source]]（`wechat_project_approval_apply.data_source`）
- [[dicts/wechat_project_approval_apply__system_delivery]]（`wechat_project_approval_apply.system_delivery`）
- [[dicts/wechat_project_approval_apply__lls_participate_role]]（`wechat_project_approval_apply.lls_participate_role`）
