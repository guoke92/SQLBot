---
type: table
title: 资方规则信息详情
page_key: funding_rule_detail
belong: tables
status: draft
anchors:
- funding_rule_detail
sources:
- database_schema:lowcode_pplatform.funding_rule_detail
- code_path:FundRuleInfoApplication.java:371
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- funding_exception_resolution
- funding_rule_front_cfg
- funding_rule_info
- funding_rule_detail__enable
- funding_rule_detail__rule_layer
---
# 资方规则信息详情

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
desc: 资方规则信息详情
inactive: false
primary_key:
- id
grain: 规则头下一字段一行明细
name_anchors:
- product_code
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: rule_value
  type: string
  desc: 规则值
- name: fund_rule_code_ref
  type: string
  desc: 关联规则信息code
- name: rule_key
  type: string
  desc: 字段key 对应front_key
- name: rule_layer
  type: string
  desc: 规则层
  dict: [FINANCING, UNDERLYING, OTHER]
  label: [融资规则, 底层规则, 其他规则]
- name: version
  type: number
  desc: 版本
- name: funding_party_mark
  type: string
  desc: 资方标识
- name: product_code
  type: string
  desc: 产品code
- name: rule_info_id
  type: number
  desc: 关系规则信息ID
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label:
  - 启用
  - 停用
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
  nullable: false
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
- name: check_scene
  type: string
  desc: 校验场景
  dict:
  - SUBMIT_VALIDATE
default_filter:
  predicate: funding_rule_detail.enable = 'Y'
  trust: confirmed
  evidence: code_path:FundRuleInfoApplication.java:371
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.id
right: funding_rule_detail.rule_info_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:FundRuleInfoApplication.java:370
source: l1_code
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
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.code
right: funding_rule_detail.fund_rule_code_ref
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:FundRuleInfoApplication.java:513
source: l1_code
join_role: identity
priority: primary
authenticity_note: 明细码引用规则头 code，与 rule_info_id 并存。
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.product_code
right: funding_rule_detail.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:规则明细产品码
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 规则明细产品码
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.product_code
right: funding_exception_resolution.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_shared_domain B↔C
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: same_semantic
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.product_code
right: funding_rule_front_cfg.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like B↔C
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: same_semantic
```

## 页面链接

### 关联表

- [[tables/funding_exception_resolution]]
- [[tables/funding_rule_front_cfg]]
- [[tables/funding_rule_info]]

### 概念

- [[concepts/funding_product_code_term]]

### 字典

- [[dicts/funding_rule_detail__rule_layer]]（`funding_rule_detail.rule_layer`）
- [[dicts/funding_rule_detail__enable]]（`funding_rule_detail.enable`）
- [[dicts/funding_rule_detail__check_scene]]（`funding_rule_detail.check_scene`）
