---
type: rule
title: 验证码有效期配置强制
page_key: verify_code_validity_config_required
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

本规则约束验证码有效期配置：发送验证码时若 `indentifycodeFacade.getIndentifyConfigDTO` 返回 null，抛出“缺少验证码有效期配置”并终止发送，无配置不允许发送。

## 需求背景

验证码发送依赖有效期配置，缺少配置时不能完成发送。相关概念 [[verify_code]]。

## 版本演进

基于 code_path:MessageFacade.sendVerifyCode 证据形成 v0.1 契约。

```ground:rule
name: 验证码有效期配置强制
content: 发送验证码时若indentifycodeFacade.getIndentifyConfigDTO返回null，抛出“缺少验证码有效期配置”并终止发送
impact: 无配置不允许发送验证码
field_targets: [IndentifycodeCofigDTO]
evidence: code_path:MessageFacade.sendVerifyCode
```