---
type: concept
title: accessToken（小程序 / 企微 / SSO）
page_key: concept/access_token
domain: 微信生态/小程序/扫脸
status: draft
aliases: [小程序 accessToken, 微信 token]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniProgramController.java
maps_to: "MiniProgramController.getOrigAccessToken：api.weixin.qq.com/cgi-bin/token，Redis key = FBP_WECHAT_TOKEN_PREFIX + appid + secret"
field_targets:
  - FBP_WECHAT_TOKEN_PREFIX+appid+secret
adjudication: boundary
also_confused_with:
  - 企业微信 access_token（WechatWorkApiClient 内部，未在本层给出）
  - SSO token
boundary: "小程序 accessToken 由 appid+secret 换取并缓存（expires_in-300 秒）；企微消息走 WechatWorkApiClient 的另一套凭证，缓存 key 与刷新逻辑不同。"
contract_version: "0.1"
---

# accessToken（小程序 / 企微 / SSO）

accessToken 有多套：小程序 accessToken（MiniProgramController 通过 appid+secret 换取，Redis key = FBP_WECHAT_TOKEN_PREFIX + appid + secret）、企微 access_token（WechatWorkApiClient 内部）、SSO token。

## 需求背景

不同通道凭证来源与刷新逻辑不同，混用会导致调用失败或串号。

## 版本演进

v0.1 区分小程序与企微两套 token 体系。

## 边界说明

小程序 accessToken 按 expires_in-300 秒缓存；企微凭证另有一套缓存 key 与刷新逻辑。

相关：[[wechat]]、[[miniprogram_access_token_cache]]、[[miniprogram_scheme_retry]]。