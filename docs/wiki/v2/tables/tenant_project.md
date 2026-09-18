---
type: table
title: 租户项目配置
page_key: tenant_project
belong: tables
status: draft
anchors: [tenant_project]
sources: ['database_schema:lowcode_pplatform.tenant_project']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_interworking_project, tenant_product, platform_product, tenant_project_approval,
  tenant_project__project_status, tenant_project__test_data, tenant_project__enable,
  tenant_project__source, tenant_project__is_prd, tenant_project__config_model, tenant_project__operater_card_type,
  tenant_project__cover_operator, tenant_project__share_flag, tenant_project__project_config_version,
  tenant_project__project_tag, tenant_project__top_flag, tenant_project__cust_oper_show,
  tenant_project__is_add]
---

# 租户项目配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### tenant

`tenant_id`, `app_tenant_code`, `db_tenant_code`, `tenant_flg_en`, `share_flag`

### project

`project_code`, `project_create_time`, `project_effective_time`, `project_agreement`, `project_status`, `project_config_version`, `project_tag`, `project_relation`, `project_approval_id`

### product

`product_id`, `channel_code`, `platform_product_code`

### ref

`ref_tenant_project_platform_product`, `ref_tenant_project_tenant_code`, `ref_tenant_project_product_code`, `refer_tenant_project_id`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `wechat_audit_no`, `wechat_audit_pass_time`

### config

`config_json`, `config_model`

### operator

`operator_id`, `operator_name`, `operator_email`, `send_email`, `operater_card_type`, `cover_operator`, `op_update_user`, `op_update_time`, `invite_customer_service_words`, `cust_oper_show`

### contact

`op_contact_a`, `op_contact_b`, `op_contact_a_group`, `verification_contact`, `verification_contact_group`, `risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`, `text`

### business

`solution_manager`, `business_manager`, `business_group`, `bussiness_project_relation`

### flags

`test_data`, `is_prd`, `top_flag`, `is_add`

### custom

`custom_field_one`, `custom_field_two`, `custom_field_three`

### misc

`organization_id`, `source_id`, `source`, `logo_path`, `first_settlement_time`

## 字段

```ground:table
table: tenant_project
database: lowcode_pplatform
description: 租户项目配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, channel_code, ref_tenant_project_tenant_code, ref_tenant_project_product_code,
  operator_name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: tenant
  title: 租户与共享
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: project
  title: 项目主档
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: product
  title: 产品与渠道
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: ref
  title: 关联引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: approval
  title: 审批信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: config
  title: 配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: operator
  title: 运营名片与运营信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: contact
  title: 对接人与组别
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: business
  title: 业务归属
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: flags
  title: 数据标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: custom
  title: 自定义字段
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project
- key: misc
  title: 其他
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: tenant_id
  data_type: number
  description: 租户编码
  cluster: tenant
- name: product_id
  data_type: number
  description: 产品编码
  cluster: product
- name: project_code
  data_type: string
  description: 项目编码
  cluster: project
- name: project_create_time
  data_type: temporal
  description: 项目创建时间
  cluster: project
- name: project_effective_time
  data_type: temporal
  description: 项目生效时间
  cluster: project
- name: channel_code
  data_type: string
  description: 渠道码
  cluster: product
- name: project_agreement
  data_type: string
  description: 项目协议
  cluster: project
- name: project_status
  data_type: string
  description: 项目状态
  cluster: project
  dictionary: tenant_project__project_status
- name: test_data
  data_type: string
  description: 是否测试数据
  cluster: flags
  dictionary: tenant_project__test_data
- name: ref_tenant_project_platform_product
  data_type: string
  description: 平台产品-项目关联
  cluster: ref
- name: ref_tenant_project_tenant_code
  data_type: string
  description: 租户-项目
  cluster: ref
- name: ref_tenant_project_product_code
  data_type: string
  description: 租户产品-项目
  cluster: ref
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_project__enable
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
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: misc
- name: platform_product_code
  data_type: string
  description: 平台产品编码
  cluster: product
- name: source_id
  data_type: string
  description: 项目来源id
  cluster: misc
- name: source
  data_type: string
  description: 项目来源
  cluster: misc
  dictionary: tenant_project__source
- name: config_json
  data_type: string
  description: 配置详情
  cluster: config
- name: operator_id
  data_type: string
  cluster: operator
- name: operator_name
  data_type: string
  cluster: operator
- name: operator_email
  data_type: string
  cluster: operator
- name: send_email
  data_type: string
  cluster: operator
- name: is_prd
  data_type: string
  description: 是否生产数据
  cluster: flags
  dictionary: tenant_project__is_prd
- name: config_model
  data_type: string
  description: 项目配置模式(XYC)
  cluster: config
  dictionary: tenant_project__config_model
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  cluster: tenant
- name: operater_card_type
  data_type: string
  description: 运营名片类型
  cluster: operator
  dictionary: tenant_project__operater_card_type
- name: cover_operator
  data_type: string
  description: 是否覆盖运营
  cluster: operator
  dictionary: tenant_project__cover_operator
- name: logo_path
  data_type: string
  description: logo路径
  cluster: misc
- name: share_flag
  data_type: string
  description: 共享租户
  cluster: tenant
  dictionary: tenant_project__share_flag
- name: project_config_version
  data_type: string
  description: 项目配置版本
  cluster: project
  dictionary: tenant_project__project_config_version
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
  cluster: contact
- name: op_contact_b
  data_type: string
  description: 运营对接人B
  cluster: contact
- name: op_contact_a_group
  data_type: string
  description: 运营组别
  cluster: contact
- name: verification_contact
  data_type: string
  description: 查验对接人
  cluster: contact
- name: verification_contact_group
  data_type: string
  description: 查验组别
  cluster: contact
- name: risk_control_contact_a
  data_type: string
  description: 风控对接人A
  cluster: contact
- name: risk_control_contact_b
  data_type: string
  description: 风控对接人B
  cluster: contact
- name: risk_control_contact_a_group
  data_type: string
  description: 风控组别
  cluster: contact
- name: solution_manager
  data_type: string
  description: 方案经理
  cluster: business
- name: business_manager
  data_type: string
  description: 业务经理
  cluster: business
- name: business_group
  data_type: string
  description: 关联业务部门
  cluster: business
- name: first_settlement_time
  data_type: temporal
  description: 首笔落地时间
  cluster: misc
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
- name: project_tag
  data_type: string
  description: 项目标签
  cluster: project
  dictionary: tenant_project__project_tag
- name: project_relation
  data_type: string
  description: 项目归属
  cluster: project
- name: bussiness_project_relation
  data_type: string
  description: 运营项目归属
  cluster: business
- name: top_flag
  data_type: string
  description: 置顶标识
  cluster: flags
  dictionary: tenant_project__top_flag
- name: text
  data_type: string
  cluster: contact
- name: op_update_user
  data_type: string
  description: 运营信息更新人
  cluster: operator
- name: op_update_time
  data_type: temporal
  description: 运营信息更新时间
  cluster: operator
- name: refer_tenant_project_id
  data_type: number
  description: 复制的租户项目
  cluster: ref
- name: invite_customer_service_words
  data_type: string
  description: 客服话术
  cluster: operator
- name: cust_oper_show
  data_type: string
  description: 建档运营名片展示
  cluster: operator
  dictionary: tenant_project__cust_oper_show
- name: is_add
  data_type: string
  description: 是否新增，Y：是，N：否，默认为N
  cluster: flags
  dictionary: tenant_project__is_add
- name: project_approval_id
  data_type: number
  description: 项目线上审批ID
  cluster: project
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_product.id
right: tenant_project.product_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.tenant_project.product_id;database_profile:lowcode_pplatform.tenant_project.product_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品编码
overlap:
  probed: true
  ratio: 1.0
  sample_size: 79
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 探测 79/79 完全覆盖(ratio 1.0)，列名 product 家族一致，两侧注释均为产品编码/产品
```

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.id
right: tenant_project.project_approval_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_project.project_approval_id;database_profile:lowcode_pplatform.tenant_project.project_approval_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: project_approval
  comment: 项目线上审批ID
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 未探测(sample_size 0)，列名与注释(项目线上审批ID)语义对应，待探测值域
```

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_project.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_project.platform_product_code;database_profile:lowcode_pplatform.tenant_project.platform_product_code
source: name
join_role: business_code
priority: secondary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 1
  miss: 1
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 名称与注释完全对应(平台产品编码)，但仅 1 个样本且 0 命中，探测量不足以定论
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_project.code
right: tenant_project.project_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project.project_code;database_profile:lowcode_pplatform.tenant_project.project_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: project
  comment: 项目编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 探测 200 样本全部未命中(ratio 0.0)，project_code 与该表 code 值域不契合
```

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_project.ref_tenant_project_platform_product
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project.ref_tenant_project_platform_product;database_profile:lowcode_pplatform.tenant_project.ref_tenant_project_platform_product
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: platform_product
  comment: 平台产品-项目关联
overlap:
  probed: true
  ratio: 0.0
  sample_size: 3
  miss: 3
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名 long_ref 指向 platform_product，但仅 3 个样本且 0 命中，样本过小不足以判 unlikely，留待扩样复核
```

## 页面链接

### 关联表

- [[tables/tenant_interworking_project]]
- [[tables/tenant_product]]
- [[tables/platform_product]]
- [[tables/tenant_project_approval]]

### 字典

- [[dicts/tenant_project__project_status]]（`tenant_project.project_status`）
- [[dicts/tenant_project__test_data]]（`tenant_project.test_data`）
- [[dicts/tenant_project__enable]]（`tenant_project.enable`）
- [[dicts/tenant_project__source]]（`tenant_project.source`）
- [[dicts/tenant_project__is_prd]]（`tenant_project.is_prd`）
- [[dicts/tenant_project__config_model]]（`tenant_project.config_model`）
- [[dicts/tenant_project__operater_card_type]]（`tenant_project.operater_card_type`）
- [[dicts/tenant_project__cover_operator]]（`tenant_project.cover_operator`）
- [[dicts/tenant_project__share_flag]]（`tenant_project.share_flag`）
- [[dicts/tenant_project__project_config_version]]（`tenant_project.project_config_version`）
- [[dicts/tenant_project__project_tag]]（`tenant_project.project_tag`）
- [[dicts/tenant_project__top_flag]]（`tenant_project.top_flag`）
- [[dicts/tenant_project__cust_oper_show]]（`tenant_project.cust_oper_show`）
- [[dicts/tenant_project__is_add]]（`tenant_project.is_add`）
