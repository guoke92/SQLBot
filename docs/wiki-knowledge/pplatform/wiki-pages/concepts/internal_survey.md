---
type: concept
title: "调研问卷"
page_key: "internal_survey"
domain: "customer_survey"
status: published
aliases: ["讯易链调研问卷", "survey", "cust_survey_answer"]
oid: 9
sources: ["db"]
contract_version: "0.1"
maps_to: "cust_survey_answer 存储的内部调研答案"
field_targets: []
adjudication: "boundary"
also_confused_with: ["问卷星活动"]
boundary: "由 /cust-web/survey 提交，写入 cust_survey_answer；问卷编码示例 XYL_2024_Q1"
scope:
  databases: [lowcode_pplatform]
---

# 调研问卷

**业务定位**：内部调研问卷，与问卷星活动区分。

## 需求背景

内部调研问卷通过 `/cust-web/survey` 提交，答案存储在 `cust_survey_answer` 表。主要用于内部业务调研，与外部问卷星系统（用于产融首页活动）在数据流和存储上相互独立。

## 版本演进

- v0.1 初稿，基于术语桥边界判定。

[[internal_survey]] [[answer_storage_granularity]]