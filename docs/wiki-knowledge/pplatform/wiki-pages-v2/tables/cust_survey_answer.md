---
type: table
title: 调研答案表
page_key: cust_survey_answer
domain: GP学习/问卷/企业画像
status: draft
anchors: [cust_survey_answer]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












本表存放落库题库问卷的作答明细：一行一个选项，多选时同一 `question_no` 会出现多行。它是「调研问卷」这条链路的答案载体，与外部问卷星的答卷数据互不读写，两者的边界见 [[concepts/wenjuan]]。当前唯一在用的问卷见口径 [[calibers/survey_code_xyl_2024_q1]]，跨租户口径见 [[calibers/survey_answer_all_tenant]]，有效记录口径见 [[calibers/cust_survey_answer_enabled]]。

## 需求背景

答案表按 `company_id + survey_code` 组成普通索引，作答主体是「当前登录企业 + 当前登录用户」，因此同一企业可以有多个用户各自提交多行答案；`other_text` 承载「其他」选项的自由文本，实测存在 '1'、'hjhh'、'饿啊讽德诵功' 等脏数据，说明该列未做输入约束。

落库路径本身未被本链路覆盖：`CustSurveyController.submit` 调用 `custSurveyAnswerService.submit(req, companyId, userId)`，但 apaas 侧 `CustSurveyAnswerService` 仅提供通用 BaseService/查询 helper，无 submit/checkPopup 实现，写值规则不可验证（见 [[rules/survey_answer_write_path_review]]）。

## 版本演进

- 当前观测：338 行，`survey_code` 恒为 `XYL_2024_Q1`，`db_tenant_code` 唯一值 `all`，`enable` 全为 `Y`。
- 代码链路中未见 `survey_code` 的常量定义，问卷范围属数据驱动。
- 字段物理类型未在语义分析证据中给出，锚点块 `type` 记为 `unknown`。

```ground:table
table: cust_survey_answer
database: lowcode_pplatform
desc: 调研答案表
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: answer_value
    type: string
    phys: varchar(512)
    desc: 选项明文，多选每个选项单独一行
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 当前登录企业ID
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "all"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: other_text
    type: string
    phys: varchar(512)
    desc: 当选项为"其他"时，填写的文本内容
  - name: question_no
    type: number
    phys: int(10)
    desc: 题号（1~N）
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: submit_time
    type: temporal
    phys: datetime
    desc: 提交时间
  - name: survey_code
    type: string
    phys: varchar(64)
    desc: 问卷code
    topk: "XYL_2024_Q1"
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: user_id
    type: number
    phys: bigint(20)
    desc: 当前登录用户ID
```