---
type: rule
title: 小程序 Scheme 生成失败重试一次
page_key: miniprogram_scheme_retry
domain: 微信生态/小程序/扫脸
status: draft
aliases: [Scheme重试, 小程序Scheme]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniProgramController.java
contract_version: "0.1"
belong: rules
---

# 小程序 Scheme 生成失败重试一次

生成小程序 Scheme 时，若首次失败（errcode≠0）且 reTry=false，则删除 Redis accessToken 缓存后以 reTry=true 重试一次；仍失败抛 IOException。expire_type=1、expire_interval=1（有效期 1 天）。

## 需求背景

token 失效是 Scheme 生成失败的主因，通过清缓存重试一次来规避。

## 版本演进

v0.1 记录重试策略与有效期参数。

```ground:rule
name: 小程序 Scheme 生成失败重试一次
content: "generateMiniProgramScheme 首次失败（errcode≠0）且 reTry=false 时，删除 Redis accessToken 缓存后以 reTry=true 重试一次；仍失败抛 IOException。expire_type=1、expire_interval=1（有效期 1 天）。"
impact: "避免 token 失效导致的 Scheme 生成失败；重试仅一次。"
field_targets:
  - FBP_WECHAT_TOKEN_PREFIX+appid+secret
evidence: code_path:MiniProgramController.java#generateMiniProgramScheme
```

相关：[[access_token]]、[[miniprogram_qrcode]]、[[miniprogram_access_token_cache]]。