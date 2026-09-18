---
type: table
title: 调研答案表
page_key: cust_survey_answer
belong: tables
status: draft
anchors: [cust_survey_answer]
sources: ['database_schema:lowcode_pplatform.cust_survey_answer']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_survey_answer__question_no, cust_survey_answer__survey_code,
  cust_survey_answer__enable, cust_survey_answer__app_tenant_code, cust_survey_answer__db_tenant_code]
---

# 调研答案表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### answer

`question_no`, `answer_value`, `other_text`, `submit_time`, `survey_code`

### subject

`company_id`, `user_id`, `organization_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: cust_survey_answer
database: lowcode_pplatform
description: 调研答案表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [survey_code, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: answer
  title: 问卷作答
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
- key: subject
  title: 提交主体与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_survey_answer
- key: tenant
  title: 租户标识
  trust: proposed
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
  cluster: subject
- name: user_id
  data_type: number
  description: 当前登录用户ID
  cluster: subject
- name: question_no
  data_type: number
  description: 题号（1~N）
  cluster: answer
  dictionary: cust_survey_answer__question_no
- name: answer_value
  data_type: string
  description: 选项明文，多选每个选项单独一行
  cluster: answer
- name: other_text
  data_type: string
  description: 当选项为"其他"时，填写的文本内容
  cluster: answer
- name: submit_time
  data_type: temporal
  description: 提交时间
  cluster: answer
- name: survey_code
  data_type: string
  description: 问卷code
  cluster: answer
  dictionary: cust_survey_answer__survey_code
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
  dictionary: cust_survey_answer__enable
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
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
  dictionary: cust_survey_answer__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: cust_survey_answer__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: subject
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_survey_answer.company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_survey_answer.company_id;database_profile:lowcode_pplatform.cust_survey_answer.company_id
source: name
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
authenticity_note: name_evidence 为家族后缀匹配（company 家族，cust_company_info.id ↔ company_id），注释「当前登录企业ID」指向企业主档；overlap
  正向 0.95（样本 60、miss 3），反向 0.0 符合答案表侧企业稀疏的正常分布，判定 likely。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_survey_answer__question_no]]（`cust_survey_answer.question_no`）
- [[dicts/cust_survey_answer__survey_code]]（`cust_survey_answer.survey_code`）
- [[dicts/cust_survey_answer__enable]]（`cust_survey_answer.enable`）
- [[dicts/cust_survey_answer__app_tenant_code]]（`cust_survey_answer.app_tenant_code`）
- [[dicts/cust_survey_answer__db_tenant_code]]（`cust_survey_answer.db_tenant_code`）
