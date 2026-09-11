---
type: caliber
title: 智能审核引流-弹出次数上限口径
page_key: calibers/gptlearn_poster_count_limit
domain: GP学习
status: draft
aliases:
  - maxPosterCount
  - 卡片弹出次数上限
  - 引流限流口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
---

# 智能审核引流-弹出次数上限口径

本口径限制[[concepts/gptlearn]]的引流卡片对同一「用户 + 企业」组合的弹出次数：按 `gpt_learn_poster_log.user_id` 与 `gpt_learn_poster_log.company_id` 聚合计数，结果必须小于 `gptLearnProperties.maxPosterCount`。作用于 `checkPosterStatus`。

因为计数对象是 [[tables/gpt_learn_poster_log]] 中的弹出记录（`popup_time` 由 `checkPosterStatus` 写入），所以「弹出记录已落库」与「用户真的看见了卡片」在本口径下是等价事件。若前端渲染失败但记录已写，额度会被消耗——这是排查「用户反馈没看到卡片但已达上限」时的关键点。

本口径与 [[calibers/gptlearn_finance_user]]（用户资格）、[[calibers/gptlearn_tenant_whitelist]]（租户白名单）串联生效，是三道门中的最后一道。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：`maxPosterCount` 的产品预期值、是否按自然日或活动周期重置。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 智能审核引流-弹出次数上限口径
predicate: count(gpt_learn_poster_log.user_id, gpt_learn_poster_log.company_id) < gptLearnProperties.maxPosterCount
scope: checkPosterStatus 引流卡片弹出校验
evidence: code_path:GptLearnService.java:checkPosterStatus
```

相关页面：[[concepts/gptlearn]]、[[tables/gpt_learn_poster_log]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_tenant_whitelist]]。