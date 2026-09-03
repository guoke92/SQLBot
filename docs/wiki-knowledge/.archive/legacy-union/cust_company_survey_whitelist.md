---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:survey-research@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 问卷星活动白名单（参与企业资格表；仓库内无业务写入口，运营经 DML/lowcode CRUD 维护）。
page_key: cust_company_survey_whitelist
domain: 问卷调研
aliases:
- cust_company_survey_whitelist
anchors:
- cust_company_survey_whitelist
---
# cust_company_survey_whitelist

问卷星活动白名单（参与企业资格表；仓库内无业务写入口，运营经 DML/lowcode CRUD 维护）。

```ground:table
table: cust_company_survey_whitelist
description: 问卷星活动白名单（参与企业资格表；仓库内无业务写入口，运营经 DML/lowcode CRUD 维护）。
inactive: false
fields: []
```

```ground:relation
type: SHARED_KEY
left: cust_company_survey_whitelist.company_id
right: cust_company_survey_state.company_id
cardinality: one_to_one
status: proposed
evidence: code_path:ev-srv-claim
```
