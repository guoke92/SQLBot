---
type: caliber
title: 调研答案跨租户口径（all）
page_key: survey_answer_all_tenant
domain: 客户管理
status: draft
aliases: [答案 all 租户口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_survey_answer.db_tenant_code
contract_version: "0.1"
belong: calibers
---

[[tables/cust_survey_answer]] 的数据被视为全租户统一，`db_tenant_code` 唯一值为 `all`（338 行）。

## 需求背景

调研答案不参与租户隔离，与 [[calibers/wenjuan_all_tenant]] 属同一设计取向：问卷类数据按「全局一份」管理。该口径由数据分布观察得到，代码侧写值点未在本链路给出（[[rules/survey_answer_write_path_review]]）。

## 版本演进

- 当前观测：`db_tenant_code` 唯一值 `all`，无其他租户样本。

```ground:caliber
name: 调研答案跨租户口径（all）
predicate: cust_survey_answer.db_tenant_code = 'all'
scope: 调研问卷答案为全租户统一数据
evidence: "db:cust_survey_answer.db_tenant_code 唯一值 all（338 行）"
```