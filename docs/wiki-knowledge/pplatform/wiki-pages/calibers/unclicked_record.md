---
type: caliber
title: "未点击记录"
page_key: unclicked_record
belong: calibers
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnPosterLogDao.java:recordClick", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 未点击记录

口径定义：click_time IS NULL 的海报埋点记录为未点击记录，点击更新仅针对未点击记录执行。

## 需求背景

为了保证一次弹卡仅记录一次点击，需要定义未点击状态，作为点击幂等更新的条件。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[gpt_learn_poster_log]] 表字段 click_time。
- [[gpt_learn_poster_log_click_state]] 状态机。
- [[click_idempotency_rule]] 使用该口径。

```ground:caliber
name: 未点击记录
predicate: "gpt_learn_poster_log.click_time IS NULL"
scope: "点击更新幂等条件，仅未点击记录可被更新为已点击"
evidence: "code_path:GptLearnPosterLogDao.java:recordClick"
```