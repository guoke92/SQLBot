---
type: table
title: 企业问卷星活动状态
page_key: cust_company_survey_state
belong: tables
status: draft
anchors: [cust_company_survey_state]
sources: ['database_schema:lowcode_pplatform.cust_company_survey_state']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_company_survey_state__first_visitor_lottery_shown,
  cust_company_survey_state__enable]
---

# 企业问卷星活动状态

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_company_survey_state
database: lowcode_pplatform
desc: 企业问卷星活动状态
inactive: false
primary_key: [id]
grain: 企业问卷星活动状态（一企一行）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: company_id
  type: number
  desc: 企业ID
- name: respondent
  type: string
  desc: 问卷星 respondent/source
- name: first_visitor_user_id
  type: number
  desc: 该企业首个进入产融首页的用户ID
- name: first_visit_time
  type: temporal
  desc: 首个用户首次访问时间
- name: first_visitor_lottery_shown
  type: string
  desc: 首个用户转盘抽奖是否已展示 Y/N
  dict: [Y]
- name: first_visitor_lottery_shown_time
  type: temporal
  desc: 首个用户转盘展示时间
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
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_survey_state.company_id
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanySurveyStateDao.java:18
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业ID
overlap:
  probed: true
  ratio: 1.0
  sample_size: 11
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 问卷星活动状态按企业主键，一企一行。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_company_survey_state__first_visitor_lottery_shown]]（`cust_company_survey_state.first_visitor_lottery_shown`）
- [[dicts/cust_company_survey_state__enable]]（`cust_company_survey_state.enable`）
