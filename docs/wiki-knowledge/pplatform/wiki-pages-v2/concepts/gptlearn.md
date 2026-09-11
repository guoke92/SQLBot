---
type: concept
title: 智能审核引流
page_key: concepts/gptlearn
domain: GP学习
status: draft
aliases:
  - GP学习
  - gptlearn
  - 引流卡片
  - 智能审核引流卡片
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:gpt_learn_poster_log
  - code:GptLearnService.java
contract_version: "0.1"
maps_to: GptLearnService + gpt_learn_poster_log + /app-web/gptlearn
field_targets:
  - gpt_learn_poster_log.popup_time
  - gpt_learn_poster_log.click_time
adjudication: synonym
also_confused_with: []
---

# 智能审核引流

「智能审核引流」是业务与前端对该功能的称呼，代码、表与接口层统一写作 `gptlearn`（接口前缀 `/app-web/gptlearn`）。同类叫法还包括 GP 学习、引流卡片、智能审核引流卡片——这些在本 wiki 中被判定为同义词（synonym），可以互相替换。参见 [[tables/gpt_learn_poster_log]]。

该概念的服务入口是 `GptLearnService`，三个接口分别是 `syncLoginInfo`（同步登录信息）、`checkPosterStatus`（检查卡片状态并写入弹出记录）、`recordPosterClick`（记录点击）。它对用户开放的前置条件是「用户为金融机构」，见 [[calibers/gptlearn_finance_user]] 与 [[rules/gptlearn_finance_user_only]]；卡片弹出还受租户白名单（[[calibers/gptlearn_tenant_whitelist]]）与弹出次数上限（[[calibers/gptlearn_poster_count_limit]]）约束。

注意本概念与问卷域的两个概念（[[concepts/cust_survey]]、[[concepts/wenjuan]]）没有业务交集，不要因为都叫「引流／问卷」而混淆。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：引流卡片指向的具体业务动作与转化目标。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/gpt_learn_poster_log]]、[[tables/cust_company_info]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]、[[rules/gptlearn_finance_user_only]]。