---
type: rule
title: 小程序 accessToken 缓存与重试
page_key: rule/miniprogram_access_token_cache
domain: 微信生态/小程序/扫脸
status: draft
aliases: [accessToken缓存, token重试]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniProgramController.java
contract_version: "0.1"
---

# 小程序 accessToken 缓存与重试

小程序 accessToken 的获取规则：以 appid+secret 为 key 查 Redis，未命中则调 api.weixin.qq.com/cgi-bin/token，失败最多重试 5 次（间隔 200ms），成功按 expires_in-300 秒缓存。

## 需求背景

频繁换取 token 会触发票据频率限制，需要缓存；网络抖动需有限重试兜底。

## 版本演进

v0.1 记录缓存 key、重试上限与缓存时长。

```ground:rule
name: 小程序 accessToken 缓存与重试
content: "以 appid+secret 为 key 查 Redis；未命中则调 api.weixin.qq.com/cgi-bin/token，失败最多重试 5 次（间隔 200ms），成功按 expires_in-300 秒缓存；未取到 access_token 时直接返回微信原始报文，5 次后抛 IOException。"
impact: "并发下多实例可能同时刷新；缓存过期窗口留 300 秒冗余。"
field_targets:
  - FBP_WECHAT_TOKEN_PREFIX+appid+secret
evidence: code_path:MiniProgramController.java#getOrigAccessToken
```

相关：[[access_token]]、[[wechat]]、[[miniprogram_scheme_retry]]。