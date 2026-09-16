---
type: table
title: 企业问卷星活动状态
page_key: cust_company_survey_state
belong: tables
status: draft
aliases: []
anchors:
- cust_company_survey_state
sources:
- database_schema:lowcode_pplatform.cust_company_survey_state
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 企业问卷星活动状态

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### survey_activity

`respondent`, `name`, `remark`

### org_relation

`company_id`, `organization_id`

### first_visitor

`first_visitor_user_id`, `first_visit_time`, `first_visitor_lottery_shown`, `first_visitor_lottery_shown_time`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: cust_company_survey_state
database: lowcode_pplatform
description: 企业问卷星活动状态
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: survey_activity
  title: 问卷活动基本信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_state
- key: org_relation
  title: 企业与机构关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_state
- key: first_visitor
  title: 首个访客埋点
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_state
- key: approval_flow
  title: 流程审批实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_state
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_survey_state
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: company_id
  data_type: number
  description: 企业ID
  nullable: true
  cluster: org_relation
- name: respondent
  data_type: string
  description: 问卷星 respondent/source
  nullable: true
  cluster: survey_activity
- name: first_visitor_user_id
  data_type: number
  description: 该企业首个进入产融首页的用户ID
  nullable: true
  cluster: first_visitor
- name: first_visit_time
  data_type: temporal
  description: 首个用户首次访问时间
  nullable: true
  cluster: first_visitor
- name: first_visitor_lottery_shown
  data_type: string
  description: 首个用户转盘抽奖是否已展示 Y/N
  nullable: true
  cluster: first_visitor
  dictionary: cust_company_survey_state_first_visitor_lottery_shown
- name: first_visitor_lottery_shown_time
  data_type: temporal
  description: 首个用户转盘展示时间
  nullable: true
  cluster: first_visitor
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: survey_activity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_company_survey_state_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: survey_activity
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: org_relation
```
