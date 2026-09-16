---
type: table
title: 调研答案表
page_key: cust_survey_answer
belong: tables
status: draft
aliases: []
anchors:
- cust_survey_answer
sources:
- database_schema:lowcode_pplatform.cust_survey_answer
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 调研答案表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### survey_answer

`question_no`, `answer_value`, `other_text`, `submit_time`, `survey_code`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### identity_context

`company_id`, `user_id`, `organization_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### basic

`name`, `remark`

## 字段

```ground:table
table: cust_survey_answer
database: lowcode_pplatform
description: 调研答案表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- survey_code
- code
- name
clusters:
- key: common
  title: 通用审计与基础字段
  include: always
- key: survey_answer
  title: 调研答题
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
- key: process
  title: 流程审批
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
- key: identity_context
  title: 组织与用户
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
- key: basic
  title: 名称备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: company_id
  data_type: number
  description: 当前登录企业ID
  nullable: true
  cluster: identity_context
- name: user_id
  data_type: number
  description: 当前登录用户ID
  nullable: true
  cluster: identity_context
- name: question_no
  data_type: number
  description: 题号（1~N）
  nullable: true
  cluster: survey_answer
- name: answer_value
  data_type: string
  description: 选项明文，多选每个选项单独一行
  nullable: true
  cluster: survey_answer
- name: other_text
  data_type: string
  description: 当选项为"其他"时，填写的文本内容
  nullable: true
  cluster: survey_answer
- name: submit_time
  data_type: temporal
  description: 提交时间
  nullable: true
  cluster: survey_answer
- name: survey_code
  data_type: string
  description: 问卷code
  nullable: true
  cluster: survey_answer
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: basic
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_survey_answer_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: basic
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
  cluster: process
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
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: identity_context
```
