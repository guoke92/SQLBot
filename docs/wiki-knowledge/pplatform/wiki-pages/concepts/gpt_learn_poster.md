---
type: concept
title: "GPT学习海报"
page_key: gpt_learn_poster
domain: gpt_learn
status: published
aliases: ["智能审核引流卡片", "引流卡片", "海报"]
oid: 1

sources: ["semantic_analysis.term_bridges", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "gpt_learn_poster_log 埋点记录及相关 GptLearnService 接口"
field_targets: []
adjudication: "synonym"
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

# GPT学习海报

GPT学习海报（又称智能审核引流卡片、引流卡片、海报）指用于 GPT 学习模块的引流卡片，通过弹卡和埋点记录追踪用户交互。

## 需求背景

业务中需要统一术语，避免海报、引流卡片等混用，因此定义标准名称及边界。

## 版本演进

- v0.1: 初始版本，来源于术语桥接分析。

## 关联

- [[gpt_learn_poster_log]] 记录海报埋点。
- [[popup_card]] 表示弹出海报的动作。
- [[tenant_whitelist_rule]]、[[popup_count_limit_rule]] 等控制海报展示。
```