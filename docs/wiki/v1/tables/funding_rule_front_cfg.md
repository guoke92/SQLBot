---
type: table
title: 资方规则前端配置页面
page_key: funding_rule_front_cfg
belong: tables
status: draft
anchors: [funding_rule_front_cfg]
sources: ['database_schema:lowcode_pplatform.funding_rule_front_cfg']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_exception_resolution, funding_rule_detail, funding_rule_info, funding_rule_front_cfg__rule_layer,
  funding_rule_front_cfg__product_code, funding_rule_front_cfg__key_type, funding_rule_front_cfg__rule_key,
  funding_rule_front_cfg__enable, funding_rule_front_cfg__check_scene]
---

# 资方规则前端配置页面

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### front_render

`front_key_name`, `front_key`, `front_field_style`

### rule_def

`rule_layer`, `key_name`, `key_type`, `rule_key`, `check_scene`

### biz_ref

`product_code`, `organization_id`

### audit

（空）

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: funding_rule_front_cfg
database: lowcode_pplatform
description: 资方规则前端配置页面
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [front_key_name, key_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: front_render
  title: 前端渲染配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: rule_def
  title: 规则定义
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: biz_ref
  title: 业务关联标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: rule_layer
  data_type: string
  description: 规则层 UNDERLYING/FINANCING
  cluster: rule_def
  dictionary: funding_rule_front_cfg__rule_layer
- name: product_code
  data_type: string
  description: 产品code
  cluster: biz_ref
  dictionary: funding_rule_front_cfg__product_code
- name: front_key_name
  data_type: string
  description: 前端展示字段名称
  cluster: front_render
- name: front_key
  data_type: string
  description: 前端字段key
  cluster: front_render
- name: front_field_style
  data_type: string
  description: 前端字段渲染json
  cluster: front_render
- name: key_name
  data_type: string
  description: 字段名称描述
  cluster: rule_def
- name: key_type
  data_type: string
  description: 字段业务规则类型
  cluster: rule_def
  dictionary: funding_rule_front_cfg__key_type
- name: rule_key
  data_type: string
  description: 规则字段key
  cluster: rule_def
  dictionary: funding_rule_front_cfg__rule_key
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
  dictionary: funding_rule_front_cfg__enable
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
  cluster: workflow
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
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: biz_ref
- name: check_scene
  data_type: string
  description: 校验场景
  cluster: rule_def
  dictionary: funding_rule_front_cfg__check_scene
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.product_code
right: funding_rule_front_cfg.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码 EQUI_JOIN，已探测重叠率 1.0（样本 2），同语义产品 code 边，可接受；本表未见指向同一父表的 id 主键边，暂不标
    secondary
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN，已探测重叠率 1.0（样本 2），同语义产品 code 边，可接受；本表未见指向同一父表的 id
  主键边，暂不标 secondary。
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.product_code
right: funding_rule_front_cfg.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码 EQUI_JOIN，重叠率 1.0（样本 2），产品 code 语义一致，可接受。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN，重叠率 1.0（样本 2），产品 code 语义一致，可接受。
```

```ground:relation
type: EQUI_JOIN
left: funding_exception_resolution.product_code
right: funding_rule_front_cfg.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码 EQUI_JOIN，重叠率 1.0（样本 2），产品 code 语义一致，可接受；跨业务域合理但需人工复核业务关系。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN，重叠率 1.0（样本 2），产品 code 语义一致，可接受；跨业务域合理但需人工复核业务关系。
```

## 页面链接

### 关联表

- [[tables/funding_exception_resolution]]
- [[tables/funding_rule_detail]]
- [[tables/funding_rule_info]]

### 字典

- [[dicts/funding_rule_front_cfg__rule_layer]]（`funding_rule_front_cfg.rule_layer`）
- [[dicts/funding_rule_front_cfg__product_code]]（`funding_rule_front_cfg.product_code`）
- [[dicts/funding_rule_front_cfg__key_type]]（`funding_rule_front_cfg.key_type`）
- [[dicts/funding_rule_front_cfg__rule_key]]（`funding_rule_front_cfg.rule_key`）
- [[dicts/funding_rule_front_cfg__enable]]（`funding_rule_front_cfg.enable`）
- [[dicts/funding_rule_front_cfg__check_scene]]（`funding_rule_front_cfg.check_scene`）
