---
type: rule
title: "调研答案存储粒度"
page_key: "answer_storage_granularity"
domain: "customer_survey"
status: published
aliases: ["调研答案存储粒度"]
oid: 18
sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_survey_answer.answer_value, cust_survey_answer.question_no]
scope:
  databases: [lowcode_pplatform]
---

# 调研答案存储粒度

**业务定位**：定义 `cust_survey_answer` 的答案存储粒度。

## 需求背景

按题号记录，选项明文，多选每个选项单独一行。`other_text` 存储其他文本，答案明细查询需按 `question_no` 聚合。

## 版本演进

- v0.1 初稿，基于 DB 证据。

```ground:rule
name: "调研答案存储粒度"
content: "cust_survey_answer 按题号记录，answer_value 为选项明文，多选每个选项单独一行；other_text 存储其他文本"
impact: "答案明细查询需按 question_no 聚合"
field_targets:
  - "cust_survey_answer.answer_value"
  - "cust_survey_answer.question_no"
evidence: "db"
```

[[internal_survey]] [[internal_survey]]

相关：[[cust_survey_answer]]
