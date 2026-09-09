---
type: rule
title: "同步登录信息加密与调用规则"
page_key: sync_login_encryption_rule
belong: rules
domain: gpt_learn
status: published
aliases: []
oid: 1

sources: ["code_path:GptLearnService.java:getAccessToken", "code_path:GptLearnService.java:buildCgiReq", "code_path:GptLearnService.java:decryptResponse", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 同步登录信息加密与调用规则

规则描述：获取 access_token 后，将登录用户信息作为请求体加密加签，调用中登同步接口，响应解密后提取 redirectUrl。该规则支持从 GPT 学习海报跳转到 SaaS 中登。

## 需求背景

用户点击海报后需要跳转到中登系统，涉及跨系统鉴权与安全，需要加密加签传输。

## 版本演进

- v0.1: 初始版本。

## 关联

- [[gpt_learn_poster]] 概念。
- [[click_idempotency_rule]] 点击后可能触发同步。
- [[cust_company_info]] 表字段 certification_no 用于同步中登接口。

```ground:rule
name: 同步登录信息加密与调用规则
content: "获取 access_token 后，将登录用户信息作为请求体加密加签，调用中登同步接口，响应解密后提取 redirectUrl"
impact: "支持从 GPT 学习海报跳转到 SaaS 中登"
field_targets: []
evidence: "code_path:GptLearnService.java:getAccessToken; GptLearnService.java:buildCgiReq; GptLearnService.java:decryptResponse"
```