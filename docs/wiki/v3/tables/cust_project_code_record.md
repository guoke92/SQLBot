---
type: table
title: 企业项目码输入记录
page_key: cust_project_code_record
belong: tables
status: draft
anchors:
- cust_project_code_record
sources:
- database_schema:lowcode_pplatform.cust_project_code_record
- code_path:CustProjectRelEnhanceService.java:410
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_company_info
- cust_project_code_record__status
- cust_project_code_record__enable
---
# 企业项目码输入记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_project_code_record
database: lowcode_pplatform
desc: 企业项目码输入记录
inactive: false
primary_key:
- id
grain: 企业录入项目码记录
name_anchors:
- code
- name
- channel_code
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
- name: company_id
  type: number
  desc: 企业id
- name: use_id
  type: number
  desc: 用户id
- name: channel_code
  type: string
  desc: 渠道码
- name: status
  type: string
  desc: 是否正确状态
  dict:
  - Y
  - N
  label: [是, 否]
- name: company_type
  type: string
  desc: 企业角色
- name: type
  type: string
  desc: 类型
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
  predicate: cust_project_code_record.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustProjectRelEnhanceService.java:410
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_code_record.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustProjectRelEnhanceService.java:407
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 0.9278
  ratio_reverse: 0.0
  sample_size: 263
  miss: 19
  deepened: true
  query_ok: true
  authenticity: unknown
authenticity_note: 项目码输入记录按企业主键。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 概念

- [[concepts/channel_code_homonym_bundle]]
- [[concepts/channel_code_term]]
- [[concepts/project_code_input]]

### 字典

- [[dicts/cust_project_code_record__status]]（`cust_project_code_record.status`）
- [[dicts/cust_project_code_record__enable]]（`cust_project_code_record.enable`）
