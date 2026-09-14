---
type: rule
title: 引流卡片弹出次数上限
page_key: poster_popup_max_count
domain: 客户管理
status: draft
aliases: [弹出上限, maxPosterCount]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:GptLearnPosterLogDao.countByUserAndCompany
contract_version: "0.1"
belong: rules
---

计数维度是 `user_id + company_id`：累计埋点行数达到 `gptLearnProperties.getMaxPosterCount()` 时返回 `notShow`，不再创建弹出记录。计数口径受 [[calibers/gpt_learn_poster_log_enabled]] 约束（只统计有效记录），状态效果见 [[processes/gpt_learn_poster_log_lifecycle]] 的 `INIT → NOT_SHOW`。

## 需求背景

该上限用来控制打扰频次，是「弹不弹」的最后一个校验点；达到上限是 `NOT_SHOW` 的第三种原因（另两种见 [[rules/gpt_learn_finance_only]] 与 [[rules/poster_allowed_tenant]]）。

## 版本演进

- 上限值由配置项 `gptLearnProperties.getMaxPosterCount()` 提供，语义分析未给出具体数值，不在本页断言。

```ground:rule
name: 引流卡片弹出次数上限
content: "同一 user_id + company_id 的埋点记录数 >= gptLearnProperties.getMaxPosterCount() 时返回 notShow，不再创建弹出记录"
impact: 控制打扰频次，决定是否新增 gpt_learn_poster_log 行
field_targets:
  - gpt_learn_poster_log.user_id
  - gpt_learn_poster_log.company_id
  - gpt_learn_poster_log.popup_time
evidence: "code_path:GptLearnService.java:checkPosterStatus + GptLearnPosterLogDao.countByUserAndCompany"
```