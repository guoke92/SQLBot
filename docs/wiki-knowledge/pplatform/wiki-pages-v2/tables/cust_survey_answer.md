---
type: table
title: cust_survey_answer（调研问卷答案）
page_key: tables/cust_survey_answer
domain: 问卷
status: draft
aliases:
  - 调研问卷答案表
  - 讯易链调研问卷答案
  - CustSurveyAnswer
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_survey_answer
  - code:CustSurveyController
  - code:CustSurveyAnswerService
contract_version: "0.1"
---


# cust_survey_answer（调研问卷答案）

本表承载「[[concepts/cust_survey]]」（调研问卷 / 讯易链调研问卷）的答卷持久化结果。它与「[[concepts/wenjuan]]」（问卷星活动）是两套彼此独立的机制：调研问卷会提交并落库答案，而问卷星活动的完成态不落库（见 [[calibers/wenjuan_no_persist_completion]]、[[concepts/survey_completed]]）。

按字段语义，一行代表「某企业某用户对某道题的某个选项」：`survey_code` 标识问卷（DB 实测为 `XYL_2024_Q1`），`question_no` 为题号（DB 实测分布 1~6），`answer_value` 存选项明文，多选题的每个选项单独占一行；当选项为「其他」时，补充文本写入 `other_text`。`company_id`/`user_id` 记录的是当前登录企业与当前登录用户，`submit_time` 为提交时间。

表带 `db_tenant_code`（实测为 `all`）、`app_tenant_code`（实测为 `base`）与 `enable`（实测均为 Y）。这三者的组合构成了本表答案数据的归属口径，见 [[calibers/survey_answer_attribution]]。

## 需求背景

本分析未提供该表的需求文档（reqdoc_claims）证据。以下问题需要业务侧确认：问卷题的题干与选项字典存放位置（本表只存选项明文，不含题目定义）、多选题拆行后如何还原为一次作答、`other_text` 在导出统计中的取值规则。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。DB 实测 `survey_code` 仅出现 `XYL_2024_Q1`，题号 1~6，可作为当前版本的样本快照，但不代表历史版本。

```ground:table
table: cust_survey_answer
database: lowcode_pplatform
desc: 调研答案表
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: answer_value
    type: string
    desc: 选项明文，多选每个选项单独一行
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: company_id
    type: number
    desc: 当前登录企业ID
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: other_text
    type: string
    desc: 当选项为"其他"时，填写的文本内容
  - name: question_no
    type: number
    desc: 题号（1~N）
  - name: remark
    type: string
    desc: remark
  - name: submit_time
    type: temporal
    desc: 提交时间
  - name: survey_code
    type: string
    desc: 问卷code
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
  - name: user_id
    type: number
    desc: 当前登录用户ID
```

相关页面：[[concepts/cust_survey]]、[[concepts/wenjuan]]、[[calibers/survey_answer_attribution]]、[[tables/cust_company_survey_state]]、[[tables/cust_company_survey_whitelist]]。