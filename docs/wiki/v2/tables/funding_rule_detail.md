---
type: table
title: 资方规则信息详情
page_key: funding_rule_detail
belong: tables
status: draft
anchors: [funding_rule_detail]
sources: ['database_schema:lowcode_pplatform.funding_rule_detail']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_rule_info, funding_rule_detail__rule_layer, funding_rule_detail__version,
  funding_rule_detail__product_code, funding_rule_detail__enable, funding_rule_detail__check_scene]
---

# 资方规则信息详情

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
desc: 资方规则信息详情
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [product_code, code, name]
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
- name: version
  type: number
  desc: 版本
  dict: ['1', '2', '3', '6', '4', '25', '9', '17', '8', '13', '23']
- name: funding_party_mark
  type: string
  desc: 资方标识
- name: product_code
  type: string
  desc: 产品code
  dict: [ACFLOW, RVSFACTOR_PC]
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
  dict: [SUBMIT_VALIDATE]
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: funding_rule_info.id
right: funding_rule_detail.rule_info_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
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
```

## 页面链接

### 关联表

- [[tables/funding_rule_info]]

### 字典

- [[dicts/funding_rule_detail__rule_layer]]（`funding_rule_detail.rule_layer`）
- [[dicts/funding_rule_detail__version]]（`funding_rule_detail.version`）
- [[dicts/funding_rule_detail__product_code]]（`funding_rule_detail.product_code`）
- [[dicts/funding_rule_detail__enable]]（`funding_rule_detail.enable`）
- [[dicts/funding_rule_detail__check_scene]]（`funding_rule_detail.check_scene`）
