---
type: table
title: 客户项目关联表
page_key: cust_project_rel
belong: tables
status: draft
anchors: [cust_project_rel]
sources: ['database_schema:lowcode_pplatform.cust_project_rel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_customized_product, cust_company_info, platform_product, cust_project_rel__company_type,
  cust_project_rel__enable, cust_project_rel__show_flag, cust_project_rel__config_model,
  cust_project_rel__status, cust_project_rel__top_flag, cust_project_rel__project_open_status]
---

# 客户项目关联表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`tenant_code`, `app_tenant_code`, `db_tenant_code`, `tenant_flg_en`

### project

`project_id`, `config_model`, `project_open_status`

### product_channel

`product_id`, `channel_code`, `ref_cust_project_rel_platform_product`

### relation

`company_type`, `ref_cust_project_rel_cust_company_info`, `organization_id`, `show_flag`, `status`, `top_flag`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### contact

`op_contact_a`, `op_contact_b`, `op_contact_a_group`, `verification_contact`, `verification_contact_group`, `risk_control_contact_a`, `risk_control_contact_b`, `risk_control_contact_a_group`

### op_update

`op_update_user`, `op_update_time`

## 字段

```ground:table
table: cust_project_rel
database: lowcode_pplatform
description: 客户项目关联表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, channel_code]
clusters:
- key: common
  title: 通用
  include: always
- key: tenant
  title: 租户与项目标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: project
  title: 项目属性
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: product_channel
  title: 产品与渠道
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: relation
  title: 关联角色与状态
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: contact
  title: 对接人与组别
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_rel
- key: op_update
  title: 运营信息更新
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: project_id
  data_type: string
  description: 项目id
  cluster: project
- name: tenant_code
  data_type: string
  description: 租户
  cluster: tenant
- name: product_id
  data_type: string
  description: 产品
  cluster: product_channel
- name: channel_code
  data_type: string
  description: 渠道码
  cluster: product_channel
- name: company_type
  data_type: string
  description: 客户角色(只取一个)
  cluster: relation
  dictionary: cust_project_rel__company_type
- name: ref_cust_project_rel_cust_company_info
  data_type: string
  description: 客户和项目关系
  cluster: relation
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_project_rel__enable
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
  cluster: relation
- name: show_flag
  data_type: string
  description: 展示标记
  cluster: relation
  dictionary: cust_project_rel__show_flag
- name: config_model
  data_type: string
  description: 项目配置模式
  cluster: project
  dictionary: cust_project_rel__config_model
- name: status
  data_type: string
  description: 关联状态
  cluster: relation
  dictionary: cust_project_rel__status
- name: ref_cust_project_rel_platform_product
  data_type: string
  description: 平台产品
  cluster: product_channel
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  cluster: tenant
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
- name: top_flag
  data_type: string
  description: 置顶标识
  cluster: relation
  dictionary: cust_project_rel__top_flag
- name: op_update_user
  data_type: string
  description: 运营信息更新人
  cluster: op_update
- name: op_update_time
  data_type: temporal
  description: 运营信息更新时间
  cluster: op_update
- name: project_open_status
  data_type: string
  description: 项目开通状态
  cluster: project
  dictionary: cust_project_rel__project_open_status
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_customized_product.id
right: cust_project_rel.product_id
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_project_rel.product_id;database_profile:lowcode_pplatform.cust_project_rel.product_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品
overlap:
  probed: true
  ratio: 0.0
  sample_size: 15
  miss: 15
  deepened: false
  query_ok: true
  authenticity: unlikely
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_rel.ref_cust_project_rel_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_cust_company_info;database_profile:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_company_info
  comment: 客户和项目关系
overlap:
  probed: true
  ratio: 0.01
  sample_size: 200
  miss: 198
  deepened: false
  query_ok: true
  authenticity: unlikely
```

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: cust_project_rel.ref_cust_project_rel_platform_product
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_platform_product;database_profile:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_platform_product
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: platform_product
  comment: 平台产品
overlap:
  probed: true
  ratio: 0.0
  sample_size: 5
  miss: 5
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/cust_customized_product]]
- [[tables/cust_company_info]]
- [[tables/platform_product]]

### 字典

- [[dicts/cust_project_rel__company_type]]（`cust_project_rel.company_type`）
- [[dicts/cust_project_rel__enable]]（`cust_project_rel.enable`）
- [[dicts/cust_project_rel__show_flag]]（`cust_project_rel.show_flag`）
- [[dicts/cust_project_rel__config_model]]（`cust_project_rel.config_model`）
- [[dicts/cust_project_rel__status]]（`cust_project_rel.status`）
- [[dicts/cust_project_rel__top_flag]]（`cust_project_rel.top_flag`）
- [[dicts/cust_project_rel__project_open_status]]（`cust_project_rel.project_open_status`）
