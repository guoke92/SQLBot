---
type: table
title: 调研答案表
page_key: cust_survey_answer
belong: tables
status: draft
anchors: [cust_survey_answer]
sources: ['database_schema:lowcode_pplatform.cust_survey_answer']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_survey_answer__question_no, cust_survey_answer__enable]
---

# 调研答案表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_survey_answer
database: lowcode_pplatform
desc: 调研答案表
inactive: false
primary_key: [id]
grain: 企业调研答题（一企一调研幂等）
name_anchors: [survey_code, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: company_id
  type: number
  desc: 当前登录企业ID
- name: user_id
  type: number
  desc: 当前登录用户ID
- name: question_no
  type: number
  desc: 题号（1~N）
  dict: ['5', '3', '6', '1', '4', '2']
- name: answer_value
  type: string
  desc: 选项明文，多选每个选项单独一行
- name: other_text
  type: string
  desc: 当选项为"其他"时，填写的文本内容
- name: submit_time
  type: temporal
  desc: 提交时间
- name: survey_code
  type: string
  desc: 问卷code
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
right: cust_survey_answer.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustSurveyAnswerDao.java:18
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 当前登录企业ID
overlap:
  probed: true
  ratio: 0.95
  ratio_reverse: 0.0
  sample_size: 60
  miss: 3
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: 调研答案按登录企业主键。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_survey_answer__question_no]]（`cust_survey_answer.question_no`）
- [[dicts/cust_survey_answer__enable]]（`cust_survey_answer.enable`）
