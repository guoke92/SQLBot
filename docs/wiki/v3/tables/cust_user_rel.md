---
type: table
title: 用户企业角色
page_key: cust_user_rel
belong: tables
status: draft
anchors: [cust_user_rel]
sources: ['database_schema:lowcode_pplatform.cust_user_rel', 'code_path:CustCompanyIfoEnchanceService.java:567']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_user_rel__company_type, cust_user_rel__type_status,
  cust_user_rel__user_type, cust_user_rel__enable]
---

# 用户企业角色

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_user_rel
database: lowcode_pplatform
desc: 用户企业角色
inactive: false
primary_key: [id]
grain: 用户企业角色（现网行极少；主路径多用 sys 侧关系）
name_anchors: [code, name, company_name]
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
- name: user_id
  type: number
  desc: 用户id
- name: company_id
  type: number
  desc: 企业id
- name: company_name
  type: string
  desc: 企业名称
- name: company_type
  type: string
  desc: 企业类型
  dict: [NULL_VALUE]
- name: type_status
  type: string
  desc: 客户角色
  dict: [EFFECT]
- name: user_type
  type: string
  desc: 联系人类型
  dict: [admin]
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
default_filter:
  predicate: cust_user_rel.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustCompanyIfoEnchanceService.java:567
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_user_rel.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyIfoEnchanceService.java:566
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 1
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 用户企业角色按企业主键。现网几乎无行；不要当成 sys 侧用户关系。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_user_rel__company_type]]（`cust_user_rel.company_type`）
- [[dicts/cust_user_rel__type_status]]（`cust_user_rel.type_status`）
- [[dicts/cust_user_rel__user_type]]（`cust_user_rel.user_type`）
- [[dicts/cust_user_rel__enable]]（`cust_user_rel.enable`）
