---
type: table
title: 资方规则信息详情
page_key: funding_rule_detail
belong: tables
status: draft
anchors: [funding_rule_detail]
sources: ['database_schema:lowcode_pplatform.funding_rule_detail']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_exception_resolution, funding_rule_info, funding_rule_front_cfg,
  funding_rule_detail__rule_layer, funding_rule_detail__version, funding_rule_detail__product_code,
  funding_rule_detail__enable, funding_rule_detail__app_tenant_code, funding_rule_detail__check_scene]
---

# 资方规则信息详情

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### rule

`rule_value`, `fund_rule_code_ref`, `rule_key`, `rule_layer`, `version`, `rule_info_id`

### funding_product

`funding_party_mark`, `product_code`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### audit

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`, `check_scene`

## 字段

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
description: 资方规则信息详情
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: rule
  title: 规则明细
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: funding_product
  title: 资方与产品
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: process
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
- key: audit
  title: 审计与租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_detail
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: rule_value
  data_type: string
  description: 规则值
  cluster: rule
- name: fund_rule_code_ref
  data_type: string
  description: 关联规则信息code
  cluster: rule
- name: rule_key
  data_type: string
  description: 字段key 对应front_key
  cluster: rule
- name: rule_layer
  data_type: string
  description: 规则层
  cluster: rule
  dictionary: funding_rule_detail__rule_layer
- name: version
  data_type: number
  description: 版本
  cluster: rule
  dictionary: funding_rule_detail__version
- name: funding_party_mark
  data_type: string
  description: 资方标识
  cluster: funding_product
- name: product_code
  data_type: string
  description: 产品code
  cluster: funding_product
  dictionary: funding_rule_detail__product_code
- name: rule_info_id
  data_type: number
  description: 关系规则信息ID
  cluster: rule
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
  dictionary: funding_rule_detail__enable
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
  cluster: process
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: audit
  dictionary: funding_rule_detail__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: audit
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
- name: check_scene
  data_type: string
  description: 校验场景
  dictionary: funding_rule_detail__check_scene
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.id
right: funding_rule_detail.rule_info_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.funding_rule_detail.rule_info_id;database_profile:lowcode_pplatform.funding_rule_detail.rule_info_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: rule_info
  comment: 关系规则信息ID
overlap:
  probed: true
  ratio: 0.7273
  ratio_reverse: 1.0
  sample_size: 33
  miss: 9
  deepened: true
  query_ok: true
  authenticity: unknown
authenticity_note: name_evidence 为家族后缀匹配（stem=rule_info），本列注释「关系规则信息ID」与父表主键语义一致；overlap
  正向 0.7273、反向 1.0（sample 33，miss 9），反向全命中、正向少量孤儿，符合子表外键指向父表主键的形态，判 likely。
```

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: funding_rule_front_cfg.product_code
right: funding_rule_detail.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_detail.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码 EQUI_JOIN，overlap 1.0，同域产品码；样本量小（2），作为跨表产品码关联的候选边保留并标注 secondary 级证据。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN，overlap 1.0，同域产品码；样本量小（2），作为跨表产品码关联的候选边保留并标注 secondary
  级证据。
```

```ground:relation
type: EQUI_JOIN
left: funding_exception_resolution.product_code
right: funding_rule_detail.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_detail.product_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码 EQUI_JOIN，overlap 1.0，同为产品码列；样本量小，证据强度有限，判为低置信码边。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN，overlap 1.0，同为产品码列；样本量小，证据强度有限，判为低置信码边。
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.code
right: funding_rule_detail.fund_rule_code_ref
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_detail.fund_rule_code_ref
source: llm
join_role: business_code
priority: secondary
name_evidence:
  match: llm_propose
  stem: fund_rule_code_ref
  comment: 码对码 EQUI_JOIN：本列注释「关联规则信息code」与父表 code 语义吻合，overlap 0.6071、反向 1.0。同表另有
    rule_info
overlap:
  probed: true
  ratio: 0.6071
  ratio_reverse: 1.0
  sample_size: 56
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN：本列注释「关联规则信息code」与父表 code 语义吻合，overlap 0.6071、反向 1.0。同表另有
  rule_info_id → funding_rule_info.id 的主键边，故该码边为 secondary 引用路径，不因是拷贝码而跳过。
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.product_code
right: funding_rule_detail.product_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.funding_rule_detail.product_code
source: llm
join_role: business_code
priority: secondary
name_evidence:
  match: llm_propose
  stem: product_code
  comment: 码对码 EQUI_JOIN，overlap 1.0，两侧注释均为「产品code」，业务语义一致；样本仅 2 个取值、比对方差弱，仅作 secondary
    码边参
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码 EQUI_JOIN，overlap 1.0，两侧注释均为「产品code」，业务语义一致；样本仅 2 个取值、比对方差弱，仅作
  secondary 码边参考，主键边仍以 rule_info_id 为准。
```

## 页面链接

### 关联表

- [[tables/funding_exception_resolution]]
- [[tables/funding_rule_info]]
- [[tables/funding_rule_front_cfg]]

### 字典

- [[dicts/funding_rule_detail__rule_layer]]（`funding_rule_detail.rule_layer`）
- [[dicts/funding_rule_detail__version]]（`funding_rule_detail.version`）
- [[dicts/funding_rule_detail__product_code]]（`funding_rule_detail.product_code`）
- [[dicts/funding_rule_detail__enable]]（`funding_rule_detail.enable`）
- [[dicts/funding_rule_detail__app_tenant_code]]（`funding_rule_detail.app_tenant_code`）
- [[dicts/funding_rule_detail__check_scene]]（`funding_rule_detail.check_scene`）
