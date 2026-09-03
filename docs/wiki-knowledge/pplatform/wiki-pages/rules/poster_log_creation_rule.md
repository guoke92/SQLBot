---
type: rule
title: "埋点记录创建规则"
page_key: poster_log_creation_rule
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnPosterLogDao.java:createPopupRecord", "code_path:GptLearnService.java:checkPosterStatus", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 埋点记录创建规则

规则描述：通过租户白名单和次数上限校验后，创建一条 enable=Y、popup_time=now、user_name/company_name/db_tenant_code 写入的海报记录，返回其 id。该规则生成弹卡展示记录。

## 需求背景

弹卡展示需要持久化埋点数据，以便后续计数和点击追踪。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[tenant_whitelist_rule]]、[[popup_count_limit_rule]] 为本规则的前置条件。
- [[gpt_learn_poster_log]] 表。
- [[popup_card]] 概念。

```ground:rule
name: 埋点记录创建规则
content: "通过租户白名单和次数上限校验后，创建一条 enable=Y、popup_time=now、user_name/company_name/db_tenant_code 写入的海报记录，返回其 id"
impact: "生成弹卡展示记录"
field_targets:
  - "gpt_learn_poster_log.user_id"
  - "gpt_learn_poster_log.company_id"
  - "gpt_learn_poster_log.user_name"
  - "gpt_learn_poster_log.company_name"
  - "gpt_learn_poster_log.popup_time"
  - "gpt_learn_poster_log.enable"
  - "gpt_learn_poster_log.db_tenant_code"
evidence: "code_path:GptLearnPosterLogDao.java:createPopupRecord; GptLearnService.java:checkPosterStatus"
```