---
type: table
title: 租户项目配置
page_key: tenant_project
belong: tables
status: draft
aliases: []
anchors:
- tenant_project
sources:
- database_schema:lowcode_pplatform.tenant_project
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### project

`name`, `project_code`, `project_agreement`, `project_status`, `project_tag`, `project_relation`, `bussiness_project_relation`

### project_time

`project_create_time`, `project_effective_time`, `first_settlement_time`

### tenant

`tenant_id`, `app_tenant_code`, `db_tenant_code`, `tenant_flg_en`, `share_flag`

### product

`product_id`, `platform_product_code`

### channel_source

`channel_code`, `source_id`, `source`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `wechat_audit_no`, `wechat_audit_pass_time`, `project_approval_id`

### config

`config_json`, `config_model`, `project_config_version`

### ref

`ref_tenant_project_platform_product`, `ref_tenant_project_tenant_code`, `ref_tenant_project_product_code`, `refer_tenant_project_id`

### operation_contact

`operator_id`, `operator_name`, `operator_email`, `op_contact_a`, `op_contact_b`, `op_contact_a_group`, `op_update_user`, `op_update_time`

### operation_show

`operater_card_type`, `cover_operator`, `logo_path`, `invite_customer_service_words`, `cust_oper_show`

### risk_verification

`verification_contact`, `verification_contact_group`, `risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`

### business

`solution_manager`, `business_manager`, `business_group`

### flags

`test_data`, `send_email`, `is_prd`, `top_flag`, `is_add`

### custom

`custom_field_one`, `custom_field_two`, `custom_field_three`

### misc

`remark`, `text`

### 未归簇

`organization_id`

## 字段

```ground:table
table: tenant_project
database: lowcode_pplatform
description: 租户项目配置
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- project_code
- channel_code
- ref_tenant_project_tenant_code
- ref_tenant_project_product_code
- platform_product_code
- operator_name
clusters:
- key: common
  title: 通用字段
  include: always
- key: project
  title: 项目主档
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: project_time
  title: 项目时间
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: product
  title: 产品
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: channel_source
  title: 渠道与来源
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: config
  title: 配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: ref
  title: 关联引用
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: operation_contact
  title: 运营对接人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: operation_show
  title: 运营展示
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: risk_verification
  title: 风控与查验
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: business
  title: 业务归属
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: flags
  title: 标识开关
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: custom
  title: 自定义字段
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: misc
  title: 备注文本
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
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
  cluster: project
- name: tenant_id
  data_type: number
  description: 租户编码
  nullable: true
  cluster: tenant
- name: product_id
  data_type: number
  description: 产品编码
  nullable: true
  cluster: product
- name: project_code
  data_type: string
  description: 项目编码
  nullable: true
  cluster: project
- name: project_create_time
  data_type: temporal
  description: 项目创建时间
  nullable: true
  cluster: project_time
- name: project_effective_time
  data_type: temporal
  description: 项目生效时间
  nullable: true
  cluster: project_time
- name: channel_code
  data_type: string
  description: 渠道码
  nullable: true
  cluster: channel_source
- name: project_agreement
  data_type: string
  description: 项目协议
  nullable: true
  cluster: project
- name: project_status
  data_type: string
  description: 项目状态
  nullable: true
  cluster: project
  dictionary: tenant_project_project_status
- name: test_data
  data_type: string
  description: 是否测试数据
  nullable: true
  cluster: flags
  dictionary: tenant_project_test_data
- name: ref_tenant_project_platform_product
  data_type: string
  description: 平台产品-项目关联
  nullable: true
  cluster: ref
- name: ref_tenant_project_tenant_code
  data_type: string
  description: 租户-项目
  nullable: true
  cluster: ref
- name: ref_tenant_project_product_code
  data_type: string
  description: 租户产品-项目
  nullable: true
  cluster: ref
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_project_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: misc
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
  description: 机构编号
  nullable: true
- name: platform_product_code
  data_type: string
  description: 平台产品编码
  nullable: true
  cluster: product
- name: source_id
  data_type: string
  description: 项目来源id
  nullable: true
  cluster: channel_source
- name: source
  data_type: string
  description: 项目来源
  nullable: true
  cluster: channel_source
- name: config_json
  data_type: string
  description: 配置详情
  nullable: true
  cluster: config
- name: operator_id
  data_type: string
  description: ''
  nullable: true
  cluster: operation_contact
- name: operator_name
  data_type: string
  description: ''
  nullable: true
  cluster: operation_contact
- name: operator_email
  data_type: string
  description: ''
  nullable: true
  cluster: operation_contact
- name: send_email
  data_type: string
  description: ''
  nullable: true
  cluster: flags
  dictionary: tenant_project_send_email
- name: is_prd
  data_type: string
  description: 是否生产数据
  nullable: true
  cluster: flags
  dictionary: tenant_project_is_prd
- name: config_model
  data_type: string
  description: 项目配置模式(XYC)
  nullable: true
  cluster: config
  dictionary: tenant_project_config_model
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  nullable: true
  cluster: tenant
- name: operater_card_type
  data_type: string
  description: 运营名片类型
  nullable: true
  cluster: operation_show
  dictionary: tenant_project_operater_card_type
- name: cover_operator
  data_type: string
  description: 是否覆盖运营
  nullable: true
  cluster: operation_show
  dictionary: tenant_project_cover_operator
- name: logo_path
  data_type: string
  description: logo路径
  nullable: true
  cluster: operation_show
- name: share_flag
  data_type: string
  description: 共享租户
  nullable: true
  cluster: tenant
  dictionary: tenant_project_share_flag
- name: project_config_version
  data_type: string
  description: 项目配置版本
  nullable: true
  cluster: config
  dictionary: tenant_project_project_config_version
- name: wechat_audit_no
  data_type: string
  description: 企微审批编号
  nullable: true
  cluster: approval
- name: wechat_audit_pass_time
  data_type: temporal
  description: 项目立项审批通过时间
  nullable: true
  cluster: approval
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
  cluster: risk_verification
- name: verification_contact_group
  data_type: string
  description: 查验组别
  nullable: true
  cluster: risk_verification
- name: risk_control_contact_a
  data_type: string
  description: 风控对接人A
  nullable: true
  cluster: risk_verification
- name: risk_control_contact_b
  data_type: string
  description: 风控对接人B
  nullable: true
  cluster: risk_verification
- name: risk_control_contact_a_group
  data_type: string
  description: 风控组别
  nullable: true
  cluster: risk_verification
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
  cluster: project_time
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
  dictionary: tenant_project_project_tag
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
- name: top_flag
  data_type: string
  description: 置顶标识
  nullable: true
  cluster: flags
  dictionary: tenant_project_top_flag
- name: text
  data_type: string
  description: ''
  nullable: true
  cluster: misc
- name: op_update_user
  data_type: string
  description: 运营信息更新人
  nullable: true
  cluster: operation_contact
- name: op_update_time
  data_type: temporal
  description: 运营信息更新时间
  nullable: true
  cluster: operation_contact
- name: refer_tenant_project_id
  data_type: number
  description: 复制的租户项目
  nullable: true
  cluster: ref
- name: invite_customer_service_words
  data_type: string
  description: 客服话术
  nullable: true
  cluster: operation_show
- name: cust_oper_show
  data_type: string
  description: 建档运营名片展示
  nullable: true
  cluster: operation_show
  dictionary: tenant_project_cust_oper_show
- name: is_add
  data_type: string
  description: 是否新增，Y：是，N：否，默认为N
  nullable: true
  cluster: flags
  dictionary: tenant_project_is_add
- name: project_approval_id
  data_type: number
  description: 项目线上审批ID
  nullable: true
  cluster: approval
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_project.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.tenant_project.platform_product_code
```
