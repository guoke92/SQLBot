---
type: caliber
title: 调研问卷-答案归属口径
page_key: survey_answer_attribution
domain: 问卷
status: draft
aliases:
  - XYL_2024_Q1 口径
  - 答案归属三条件
  - 调研问卷有效答案口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_survey_answer
contract_version: "0.1"
belong: calibers
---

# 调研问卷-答案归属口径

本口径界定哪些行构成「[[concepts/cust_survey]]（讯易链调研问卷）的有效答案数据」：`survey_code = 'XYL_2024_Q1'`、`db_tenant_code = 'all'`、`enable = 'Y'` 三者同时成立。三者分别锚定问卷身份、租户归属与逻辑有效性。

在 [[tables/cust_survey_answer]] 中，这三列并非总是这个取值——`app_tenant_code` 实测为 `base`、`db_tenant_code` 实测为 `all`，而其它表的 `db_tenant_code` 实测值各不相同（例如 [[tables/cust_company_survey_state]] 为 LN1/all，[[tables/cust_company_survey_whitelist]] 为 LN1）。因此按本口径取数时不应使用统一的租户过滤条件。

本口径是纯 DB 口径（证据来源为 db，不含代码路径），与「完成态不落库」的问卷星活动（[[calibers/wenjuan_no_persist_completion]]）在数据来源上完全不同。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：`survey_code` 未来新增问卷时的命名规范与历史问卷的并存方式。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。DB 实测样本仅覆盖 `XYL_2024_Q1` 与题号 1~6。

```ground:caliber
name: 调研问卷-答案归属口径
predicate: cust_survey_answer.survey_code = 'XYL_2024_Q1' AND cust_survey_answer.db_tenant_code = 'all' AND cust_survey_answer.enable = 'Y'
scope: 讯易链调研问卷答案数据
evidence: db
```

相关页面：[[concepts/cust_survey]]、[[tables/cust_survey_answer]]、[[calibers/wenjuan_no_persist_completion]]、[[concepts/survey_completed]]。