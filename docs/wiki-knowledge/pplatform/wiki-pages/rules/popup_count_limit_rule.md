---
type: rule
title: "弹卡次数上限规则"
page_key: popup_count_limit_rule
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnPosterLogDao.java:countByUserAndCompany", "code_path:GptLearnService.java:checkPosterStatus", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 弹卡次数上限规则

规则描述：同一 userId + companyId 下 enable=Y 的记录数大于等于 maxPosterCount 时不再弹卡。该规则限制单个用户在企业维度上的海报弹卡频率。

## 需求背景

为避免过度打扰用户，需要控制弹卡频率，通过计数已有效弹出的次数实现上限限制。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[valid_poster_impression_record]] 口径用于计数。
- [[gpt_learn_poster_log]] 表字段 user_id、company_id、enable。
- [[poster_log_creation_rule]] 在满足上限条件后创建记录。

```ground:rule
name: 弹卡次数上限规则
content: "同一 userId + companyId 下 enable=Y 的记录数大于等于 maxPosterCount 时不再弹卡"
impact: "限制单个用户在企业维度上的海报弹卡频率"
field_targets:
  - "gpt_learn_poster_log.user_id"
  - "gpt_learn_poster_log.company_id"
  - "gpt_learn_poster_log.enable"
evidence: "code_path:GptLearnPosterLogDao.java:countByUserAndCompany; GptLearnService.java:checkPosterStatus"
```