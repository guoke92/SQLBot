---
type: caliber
title: 智能审核引流-金融机构用户口径
page_key: gptlearn_finance_user
domain: GP学习
status: draft
aliases:
  - FINANCE 用户口径
  - validateFinanceUser
  - 金融机构用户校验
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
belong: calibers
---

# 智能审核引流-金融机构用户口径

本口径规定「谁能用[[concepts/gptlearn]]」。判定条件是当前登录用户的企业角色为金融机构：`companyType = 'FINANCE'`（字段落点见 [[tables/cust_company_info]] 的 `custCompanyType`，代码按 JSON 数组字符串处理）。

适用范围是 `GptLearnService` 的全部接口：`syncLoginInfo`、`checkPosterStatus`、`recordPosterClick`。实现集中在 `validateFinanceUser`。这是一道前置闸门：用户校验不过，后续的白名单租户口径（[[calibers/gptlearn_tenant_whitelist]]）与弹出次数上限口径（[[calibers/gptlearn_poster_count_limit]]）都不会被评估，也不会向 [[tables/gpt_learn_poster_log]] 写入记录。

与之配套的强制规则见 [[rules/gptlearn_finance_user_only]]。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：企业存在多个角色（`custCompanyType` 为多元素 JSON 数组）时，是否只要包含 `FINANCE` 即通过。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 智能审核引流-金融机构用户口径
predicate: "当前登录用户.companyType = 'FINANCE'"
scope: GptLearnService 全部接口：syncLoginInfo、checkPosterStatus、recordPosterClick
evidence: code_path:GptLearnService.java:validateFinanceUser
```

相关页面：[[concepts/gptlearn]]、[[tables/gpt_learn_poster_log]]、[[tables/cust_company_info]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]、[[rules/gptlearn_finance_user_only]]。