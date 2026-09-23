---
type: table
title: 资方规则信息
page_key: funding_rule_info
belong: tables
status: draft
anchors:
- funding_rule_info
sources:
- database_schema:lowcode_pplatform.funding_rule_info
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- funding_exception_resolution
- funding_rule_detail
- funding_rule_front_cfg
- platform_product
- funding_rule_info__rule_status
- funding_rule_info__enable
---
# 资方规则信息

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: funding_rule_info
database: lowcode_pplatform
desc: 资方规则信息
inactive: false
primary_key:
- id
grain: 一产品一资金方一行规则头
name_anchors:
- funding_party_name
- product_code
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: funding_party_mark
  type: string
  desc: 资金方标识
- name: funding_party_name
  type: string
  desc: 资方名称
- name: product_code
  type: string
  desc: 产品code
- name: rule_status
  type: string
  desc: 规则状态 ACTIVE/INACTIVE/PENDING
  dict:
  - PENDING
  - ACTIVE
  - INACTIVE
  label:
  - 待生效
  - 生效中
  - 已失效
  written_with:
  - update_by
  - update_user
  - update_time
- name: version
  type: number
  desc: 版本号
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
  label: [启用, 停用]
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
  written_with:
  - rule_status
  - update_user
  - update_time
- name: update_user
  type: string
  desc: 更新人名称
  written_with:
  - rule_status
  - update_by
  - update_time
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
  written_with:
  - rule_status
  - update_by
  - update_user
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
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.product_code
right: funding_exception_resolution.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:资金方异常解析
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 资金方异常解析
```

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
left: funding_rule_info.product_code
right: funding_rule_front_cfg.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:资方规则前端配置
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 资方规则前端配置
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.product_code
right: funding_rule_info.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_hub_fk L→R=1.0
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: same_semantic+live
```

## 页面链接

### 关联表

- [[tables/funding_exception_resolution]]
- [[tables/funding_rule_detail]]
- [[tables/funding_rule_front_cfg]]
- [[tables/platform_product]]

### 概念

- [[concepts/funding_product_code_term]]
- [[concepts/funding_rule_active]]

### 字典

- [[dicts/funding_rule_info__rule_status]]（`funding_rule_info.rule_status`）
- [[dicts/funding_rule_info__enable]]（`funding_rule_info.enable`）
