---
type: caliber
title: 引流卡片埋点有效记录口径
page_key: gpt_learn_poster_log_enabled
domain: 客户管理
status: draft
aliases: [埋点有效口径, poster enable 口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - db:gpt_learn_poster_log.enable
contract_version: "0.1"
belong: calibers
---

[[tables/gpt_learn_poster_log]] 的有效记录口径为 `enable = 'Y'`：弹出次数统计 `countByUserAndCompany` 与点击记录 `recordClick` 都以此为准，直接影响 [[rules/poster_popup_max_count]] 的计数结果与 [[processes/gpt_learn_poster_log_lifecycle]] 的状态推进。

## 需求背景

弹出上限按「同一用户 + 同一企业」累计，若无效记录被计入会提前触发 `NOT_SHOW`，因此有效标记是计数口径的一部分。当前实测 252 行全为 `Y`，逻辑删除尚未被实际使用。

## 版本演进

- 当前观测：`enable` 全 `Y`（252 行），与 [[enums/gpt_learn_poster_log_enable]] 一致。

```ground:caliber
name: 引流卡片埋点有效记录
predicate: gpt_learn_poster_log.enable = 'Y'
scope: 弹出次数统计 countByUserAndCompany 与点击记录 recordClick
evidence: "code_path:GptLearnService.java:checkPosterStatus + db:gpt_learn_poster_log.enable 全 Y（252 行）"
```