---
type: caliber
title: 当前唯一在用问卷口径
page_key: survey_code_xyl_2024_q1
domain: 客户管理
status: draft
aliases: [XYL_2024_Q1, 在用问卷口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_survey_answer.survey_code
contract_version: "0.1"
belong: calibers
---

调研答案的问卷范围口径为 `survey_code = 'XYL_2024_Q1'`：全表唯一值，共 338 行。

## 需求背景

该问卷编码在代码链路中没有常量定义，属数据驱动——问卷的增删改由数据侧决定，代码无需发布即可切换问卷范围。术语边界见 [[concepts/wenjuan]]。

## 版本演进

- 当前观测：`survey_code` 唯一值 `XYL_2024_Q1`，尚无第二份问卷样本。

```ground:caliber
name: 当前唯一在用问卷
predicate: cust_survey_answer.survey_code = 'XYL_2024_Q1'
scope: 调研问卷答案范围（代码中未常量定义，属数据驱动）
evidence: "db:cust_survey_answer.survey_code 唯一值 XYL_2024_Q1（338 行）"
```