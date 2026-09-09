---
type: rule
title: "点击记录幂等规则"
page_key: click_idempotency_rule
belong: rules
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnPosterLogDao.java:recordClick", "code_path:GptLearnService.java:recordPosterClick", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 点击记录幂等规则

规则描述：仅当记录 id、userId、companyId 三条件匹配且 click_time IS NULL 时，更新 click_time 为当前时间；更新失败则抛“埋点记录不存在或已记录点击”。该规则保证一次弹卡仅记录一次点击。

## 需求背景

需要防止重复点击导致数据污染，通过条件更新实现幂等性。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[unclicked_record]] 口径提供前置条件。
- [[gpt_learn_poster_log_click_state]] 状态机描述状态转换。
- [[gpt_learn_poster_log]] 表。

```ground:rule
name: 点击记录幂等规则
content: "仅当记录 id、userId、companyId 三条件匹配且 click_time IS NULL 时，更新 click_time 为当前时间；更新失败则抛“埋点记录不存在或已记录点击”"
impact: "保证一次弹卡仅记录一次点击"
field_targets:
  - "gpt_learn_poster_log.id"
  - "gpt_learn_poster_log.user_id"
  - "gpt_learn_poster_log.company_id"
  - "gpt_learn_poster_log.click_time"
evidence: "code_path:GptLearnPosterLogDao.java:recordClick; GptLearnService.java:recordPosterClick"
```