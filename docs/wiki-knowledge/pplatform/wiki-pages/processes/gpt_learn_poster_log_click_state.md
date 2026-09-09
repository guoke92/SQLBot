---
type: process
title: "gpt_learn_poster_log.click_state"
page_key: gpt_learn_poster_log_click_state
belong: processes
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["db_dist", "code_enum", "code_path:GptLearnPosterLogDao.java:recordClick", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# gpt_learn_poster_log.click_state

点击状态机描述海报埋点记录的点击状态：未点击（click_time 为 null）与已点击（click_time 为日期时间）之间的转换。

## 需求背景

弹卡埋点需要区分用户是否点击了卡片，以便后续分析点击率和防止重复点击。状态转换通过 recordClick 方法实现。

## 版本演进

- v0.1: 初始版本，定义点击状态及转换。

## 关联

- [[gpt_learn_poster_log]] 表字段 click_time 承载状态。
- [[click_idempotency_rule]] 约束转换条件。
- [[unclicked_record]] 口径定义未点击状态的判定。

```ground:process
name: gpt_learn_poster_log.click_state
field: gpt_learn_poster_log.click_time
states:
  - value: null
    label: "未点击"
    source: "db_dist"
  - value: "<datetime>"
    label: "已点击"
    source: "code_enum"
transitions:
  - from: null
    event: "用户点击海报卡片，调用 recordPosterClick"
    to: "<datetime>"
    evidence: "code_path:GptLearnPosterLogDao.java:recordClick"
```