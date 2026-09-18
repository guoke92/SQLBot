---
type: table
title: 租户项目配置
page_key: tenant_project
belong: tables
status: draft
anchors: [tenant_project]
sources: ['database_schema:lowcode_pplatform.tenant_project', 'code_path:TenantProjectDaoImpl.java:36']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_company, ca_fee_order, ca_fee_project_config, cust_project_pushcust,
  cust_project_rel, tenant_interworking_project, tenant_product, tenant_project_approval,
  platform_product, tenant_setting_config, tenant_project__project_status, tenant_project__test_data,
  tenant_project__enable, tenant_project__source, tenant_project__is_prd, tenant_project__config_model,
  tenant_project__operater_card_type, tenant_project__cover_operator, tenant_project__share_flag,
  tenant_project__project_config_version, tenant_project__project_tag, tenant_project__top_flag,
  tenant_project__cust_oper_show, tenant_project__is_add]
---

# 租户项目配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project
database: lowcode_pplatform
desc: 租户项目配置
inactive: false
primary_key: [id]
grain: 一租户项目一行
name_anchors: [code, name, channel_code, ref_tenant_project_tenant_code, ref_tenant_project_product_code,
  operator_name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: tenant_id
  type: number
  desc: 租户编码
- name: product_id
  type: number
  desc: 产品编码
- name: project_code
  type: string
  desc: 项目编码
- name: project_create_time
  type: temporal
  desc: 项目创建时间
- name: project_effective_time
  type: temporal
  desc: 项目生效时间
- name: channel_code
  type: string
  desc: 渠道码
- name: project_agreement
  type: string
  desc: 项目协议
- name: project_status
  type: string
  desc: 项目状态
  dict: ['1', '0', '2']
  label: [已生效, 待生效, 已失效]
- name: test_data
  type: string
  desc: 是否测试数据
  dict: [N, Y]
- name: ref_tenant_project_platform_product
  type: string
  desc: 平台产品-项目关联
- name: ref_tenant_project_tenant_code
  type: string
  desc: 租户-项目
- name: ref_tenant_project_product_code
  type: string
  desc: 租户产品-项目
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
- name: platform_product_code
  type: string
  desc: 平台产品编码
- name: source_id
  type: string
  desc: 项目来源id
- name: source
  type: string
  desc: 项目来源
  dict: [pplatform, ACFLOW, RVSFACTOR_PC, ORDER, STORAGE]
- name: config_json
  type: string
  desc: 配置详情
- name: operator_id
  type: string
- name: operator_name
  type: string
- name: operator_email
  type: string
- name: send_email
  type: string
- name: is_prd
  type: string
  desc: 是否生产数据
  dict: [Y, N]
- name: config_model
  type: string
  desc: 项目配置模式(XYC)
  dict: [admin, normal]
- name: tenant_flg_en
  type: string
  desc: 项目标识（英文）
- name: operater_card_type
  type: string
  desc: 运营名片类型
  dict: [WX_WORK, WX]
- name: cover_operator
  type: string
  desc: 是否覆盖运营
  dict: [Y, N]
- name: logo_path
  type: string
  desc: logo路径
- name: share_flag
  type: string
  desc: 共享租户
  dict: [N, Y]
- name: project_config_version
  type: string
  desc: 项目配置版本
  dict: [config, configPro]
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
  dict: [PRD, TEST]
- name: project_relation
  type: string
  desc: 项目归属
- name: bussiness_project_relation
  type: string
  desc: 运营项目归属
- name: top_flag
  type: string
  desc: 置顶标识
  dict: ['0', '1']
- name: text
  type: string
- name: op_update_user
  type: string
  desc: 运营信息更新人
- name: op_update_time
  type: temporal
  desc: 运营信息更新时间
- name: refer_tenant_project_id
  type: number
  desc: 复制的租户项目
- name: invite_customer_service_words
  type: string
  desc: 客服话术
- name: cust_oper_show
  type: string
  desc: 建档运营名片展示
  dict: [Y, N]
- name: is_add
  type: string
  desc: 是否新增，Y：是，N：否，默认为N
  dict: [N, Y]
  label: [否, 是]
- name: project_approval_id
  type: number
  desc: 项目线上审批ID
default_filter:
  predicate: tenant_project.enable = 'Y'
  trust: confirmed
  evidence: code_path:TenantProjectDaoImpl.java:36
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_product.id
right: tenant_project.product_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProjectDaoImpl.java:34
source: l1_code
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
authenticity_note: 项目按租户产品主键关联。
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_project.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProjectDomainService.java:157
source: l1_code
join_role: identity
priority: primary
authenticity_note: 创建项目写 tenant_id=租户配置主键；列表按 tenant_id 等值查。
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.code
right: tenant_project.ref_tenant_project_tenant_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProjectDaoImpl.java:135
source: l1_code
join_role: identity
priority: primary
authenticity_note: 生效项目列表按租户配置 code 过滤。
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.code
right: tenant_project.ref_tenant_project_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProjectDaoImpl.java:136
source: l1_code
join_role: identity
priority: primary
authenticity_note: 码引用租户产品 code。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.id
right: tenant_project.project_approval_id
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:405
source: l1_code
join_role: identity
priority: secondary
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
authenticity_note: 创建审批后回写项目上的审批主键。主查询走 code=ref。
```

### unknown — 待复核

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

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[tables/ca_fee_project_config]]
- [[tables/cust_project_pushcust]]
- [[tables/cust_project_rel]]
- [[tables/tenant_interworking_project]]
- [[tables/tenant_product]]
- [[tables/tenant_project_approval]]
- [[tables/platform_product]]
- [[tables/tenant_setting_config]]

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
