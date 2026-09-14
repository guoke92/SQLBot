---
type: rule
title: 智能审核引流仅金融机构用户可用
page_key: gptlearn_finance_user_only
domain: GP学习
status: draft
aliases:
  - validateFinanceUser 规则
  - FINANCE 前置校验
  - 引流接口准入规则
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
belong: rules
---

# 智能审核引流仅金融机构用户可用

这是一条强制的接口准入规则：`validateFinanceUser` 校验当前登录用户非空、`companyType` 为 `FINANCE`、且企业信息存在，任一不满足即抛异常。它保护的是 [[concepts/gptlearn]] 的全部三个接口。

规则的影响面是明确的：非金融机构用户无法调用 `/app-web/gptlearn/**` 下的同步登录、检查卡片、记录点击接口，因而也不会在 [[tables/gpt_learn_poster_log]] 中产生任何记录。字段落点为 [[tables/cust_company_info]] 的 `custCompanyType`，口径表述见 [[calibers/gptlearn_finance_user]]。

需要区分「规则」与「口径」：规则描述的是校验行为与失败后果（抛异常、接口不可用），口径描述的是判定谓词本身。两者证据同源，但使用场景不同——排查接口报错看本页，统计投放范围看口径页。

## 需求背景

本分析未提供本规则的需求文档（reqdoc_claims）证据。待业务补充：异常抛出后的前端提示话术与埋点。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:rule
name: 智能审核引流仅金融机构用户可用
content: validateFinanceUser 校验当前登录用户非空、companyType 为 FINANCE、企业信息存在，否则抛异常。
impact: 非金融机构用户无法调用 /app-web/gptlearn/** 下同步登录、检查卡片、记录点击接口。
field_targets:
  - cust_company_info.custCompanyType
evidence: code_path:GptLearnService.
```

相关页面：[[concepts/gptlearn]]、[[calibers/gptlearn_finance_user]]、[[tables/cust_company_info]]、[[tables/gpt_learn_poster_log]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]。