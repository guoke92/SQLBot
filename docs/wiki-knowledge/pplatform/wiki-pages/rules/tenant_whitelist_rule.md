---
type: rule
title: "弹卡租户白名单规则"
page_key: tenant_whitelist_rule
belong: rules
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnService.java:checkPosterStatus", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 弹卡租户白名单规则

规则描述：若当前企业的 db_tenant_code 不在 gptLearnProperties 配置的允许租户白名单内，则 checkPosterStatus 返回不展示。该规则控制哪些租户可弹出海报卡片。

## 需求背景

海报弹卡需要限制在特定租户范围内，通过配置文件白名单进行控制。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[cust_company_info]] 表字段 db_tenant_code。
- [[tenant_code]] 概念。
- [[gpt_learn_poster]] 概念。
- [[poster_log_creation_rule]] 依赖本规则的前提。

```ground:rule
name: 弹卡租户白名单规则
content: "若当前企业的 db_tenant_code 不在 gptLearnProperties 配置的允许租户白名单内，则 checkPosterStatus 返回不展示"
impact: "控制哪些租户可弹出海报卡片"
field_targets:
  - "cust_company_info.db_tenant_code"
evidence: "code_path:GptLearnService.java:checkPosterStatus"
```