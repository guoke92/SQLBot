---
type: dict
title: gpt_learn_poster_log.enable
page_key: gpt_learn_poster_log__enable
belong: dicts
status: draft
anchors: [gpt_learn_poster_log.enable]
sources: ['database_profile:gpt_learn_poster_log.enable', 'database_schema:gpt_learn_poster_log.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [gpt_learn_poster_log]
---

# gpt_learn_poster_log.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `gpt_learn_poster_log.enable`，表页 [[tables/gpt_learn_poster_log]]。

## 取值

```ground:dict
dict: gpt_learn_poster_log__enable
fields: [gpt_learn_poster_log.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
