---
type: table
title: 资方规则信息
page_key: funding_rule_info
belong: tables
status: draft
anchors: [funding_rule_info]
sources: ['database_schema:lowcode_pplatform.funding_rule_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_exception_resolution, funding_rule_detail, funding_rule_front_cfg,
  funding_rule_info__product_code, funding_rule_info__rule_status, funding_rule_info__version,
  funding_rule_info__enable, funding_rule_info__app_tenant_code]
---

# 资方规则信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### funding_rule

`funding_party_mark`, `funding_party_name`, `product_code`, `rule_status`, `version`, `organization_id`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: funding_rule_info
database: lowcode_pplatform
description: 资方规则信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [funding_party_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: funding_rule
  title: 资方规则主体
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_info
- key: approval
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: funding_party_mark
  data_type: string
  description: 资金方标识
  cluster: funding_rule
- name: funding_party_name
  data_type: string
  description: 资方名称
  cluster: funding_rule
- name: product_code
  data_type: string
  description: 产品code
  cluster: funding_rule
  dictionary: funding_rule_info__product_code
- name: rule_status
  data_type: string
  description: 规则状态 ACTIVE/INACTIVE/PENDING
  cluster: funding_rule
  dictionary: funding_rule_info__rule_status
- name: version
  data_type: number
  description: 版本号
  cluster: funding_rule
  dictionary: funding_rule_info__version
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
  dictionary: funding_rule_info__enable
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
  dictionary: funding_rule_info__app_tenant_code
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
  cluster: funding_rule
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.product_code
right: funding_rule_info.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_info.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码，同名产品code，overlap=1.0（样本2），可作 EQUI_JOIN；同表 id 边 overlap=0 未成立，本边为当前有效码边。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码，同名产品code，overlap=1.0（样本2），可作 EQUI_JOIN；同表 id 边 overlap=0 未成立，本边为当前有效码边。
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_front_cfg.product_code
right: funding_rule_info.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_info.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码，同名产品code，overlap=1.0（样本2），可作合法 EQUI_JOIN。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码，同名产品code，overlap=1.0（样本2），可作合法 EQUI_JOIN。
```

```ground:relation
type: EQUI_JOIN
left: funding_exception_resolution.product_code
right: funding_rule_info.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_info.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码，同名产品code，overlap=1.0（样本2），接受为 EQUI_JOIN。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码，同名产品code，overlap=1.0（样本2），接受为 EQUI_JOIN。
```

## 页面链接

### 关联表

- [[tables/funding_exception_resolution]]
- [[tables/funding_rule_detail]]
- [[tables/funding_rule_front_cfg]]

### 字典

- [[dicts/funding_rule_info__product_code]]（`funding_rule_info.product_code`）
- [[dicts/funding_rule_info__rule_status]]（`funding_rule_info.rule_status`）
- [[dicts/funding_rule_info__version]]（`funding_rule_info.version`）
- [[dicts/funding_rule_info__enable]]（`funding_rule_info.enable`）
- [[dicts/funding_rule_info__app_tenant_code]]（`funding_rule_info.app_tenant_code`）
