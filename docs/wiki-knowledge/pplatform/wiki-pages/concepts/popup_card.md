---
type: concept
title: "弹卡"
page_key: popup_card
belong: concepts
domain: gpt_learn
status: published
aliases: ["弹出引流卡片", "弹出海报"]
oid: 1

sources: ["semantic_analysis.term_bridges", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "checkPosterStatus 创建 gpt_learn_poster_log 记录"
field_targets: []
adjudication: "synonym"
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

# 弹卡

弹卡指弹出引流卡片（弹出海报）的动作，通过 checkPosterStatus 接口创建 gpt_learn_poster_log 记录，并以 popup_time 标记弹出时间，enable=Y 表示有效记录。

## 需求背景

需要准确定义弹卡行为，与点击行为区分，作为埋点日志的起点。

## 版本演进

- v0.1: 初始版本，来源于术语桥接分析。

## 关联

- [[gpt_learn_poster]] 为同义词。
- [[gpt_learn_poster_log]] 记录弹卡。
- [[poster_log_creation_rule]] 定义弹卡记录创建。
```