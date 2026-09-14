---
type: caliber
title: 调研答案有效记录口径
page_key: cust_survey_answer_enabled
domain: 客户管理
status: draft
aliases: [答案有效口径, answer enable 口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_survey_answer.enable
contract_version: "0.1"
belong: calibers
---

[[tables/cust_survey_answer]] 的查询口径为 `enable = 'Y'`，用于调研问卷答案范围过滤。

## 需求背景

答案表按企业 + 问卷 + 用户组织，逻辑有效标记用于在不物理删除的前提下剔除历史/作废答案。写值点未在本链路给出（[[rules/survey_answer_write_path_review]]），因此 `enable` 的赋值行为无法核对。

## 版本演进

- 当前观测：338 行全为 `Y`，未见 `N` 样本。

```ground:caliber
name: 调研答案有效记录
predicate: cust_survey_answer.enable = 'Y'
scope: 调研问卷答案查询
evidence: "db:cust_survey_answer.enable 全 Y（338 行）"
```