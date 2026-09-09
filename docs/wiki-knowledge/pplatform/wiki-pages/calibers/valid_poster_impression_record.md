---
type: caliber
title: "有效海报埋点记录"
page_key: valid_poster_impression_record
belong: calibers
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnPosterLogDao.java:countByUserAndCompany", "db_dist:enable=Y", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 有效海报埋点记录

口径定义：enable = 'Y' 的海报埋点记录为有效记录，用于同一用户+企业维度的弹卡计数及有效记录识别。

## 需求背景

弹卡次数限制需要准确计数有效展示，且后续分析需要区分有效和无效数据，因此定义有效口径。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[gpt_learn_poster_log]] 表字段 enable。
- [[popup_count_limit_rule]] 使用该口径进行计数。

```ground:caliber
name: 有效海报埋点记录
predicate: "gpt_learn_poster_log.enable = 'Y'"
scope: "用于同一用户+企业维度的弹卡计数，以及识别有效弹卡记录"
evidence: "code_path:GptLearnPosterLogDao.java:countByUserAndCompany; db_dist:enable=Y"
```