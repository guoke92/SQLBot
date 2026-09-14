---
type: caliber
title: 智能审核引流-租户白名单口径
page_key: gptlearn_tenant_whitelist
domain: GP学习
status: draft
aliases:
  - posterAllowedTenant
  - 引流租户白名单
  - 投放租户口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
belong: calibers
---

# 智能审核引流-租户白名单口径

本口径规定哪些租户可以收到[[concepts/gptlearn]]的引流卡片：企业的 `cust_company_info.db_tenant_code` 必须属于 `gptLearnProperties.posterAllowedTenant` 配置的白名单集合。它只作用于 `checkPosterStatus`（引流卡片弹出校验）这一个环节，不覆盖 `syncLoginInfo` 与 `recordPosterClick`。

与它并列的还有两道门：用户侧见 [[calibers/gptlearn_finance_user]]，次数侧见 [[calibers/gptlearn_poster_count_limit]]。三者同时满足时，`checkPosterStatus` 才会创建弹出记录并写入 [[tables/gpt_learn_poster_log]] 的 `popup_time`。

注意本口径使用 `db_tenant_code`（数据租户标识）而非 `app_tenant_code`（逻辑租户标识）；这两个字段在各表中并存，口径选择哪一个直接决定命中范围。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：`posterAllowedTenant` 的配置载体与变更流程。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 智能审核引流-租户白名单口径
predicate: cust_company_info.db_tenant_code 属于 gptLearnProperties.posterAllowedTenant
scope: checkPosterStatus 引流卡片弹出校验
evidence: code_path:GptLearnService.java:checkPosterStatus
```

相关页面：[[concepts/gptlearn]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_poster_count_limit]]、[[tables/gpt_learn_poster_log]]、[[tables/cust_company_info]]。