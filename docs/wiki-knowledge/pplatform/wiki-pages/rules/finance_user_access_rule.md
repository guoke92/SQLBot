---
type: rule
title: "金融机构用户准入规则"
page_key: finance_user_access_rule
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnService.java:validateFinanceUser", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 金融机构用户准入规则

规则描述：当前登录用户必须存在且 companyType = FINANCE，否则抛业务异常；同时企业信息必须存在。该规则拦截非金融机构用户访问 GPT 学习海报相关接口。

## 需求背景

GPT学习海报功能仅面向金融机构用户，需要前置校验用户类型和企业信息，保障业务合规与安全。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[gpt_learn_poster]] 概念。
- [[tenant_whitelist_rule]] 后续校验。
- [[gpt_learn_poster_log]] 表。

```ground:rule
name: 金融机构用户准入规则
content: "当前登录用户必须存在且 companyType = FINANCE，否则抛业务异常；同时企业信息必须存在"
impact: "拦截非金融机构用户访问 GPT 学习海报相关接口"
field_targets:
  - "LoginUser.companyType"
evidence: "code_path:GptLearnService.java:validateFinanceUser"
```