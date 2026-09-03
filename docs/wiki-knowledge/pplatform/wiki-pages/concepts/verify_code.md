---
type: concept
title: 验证码
page_key: verify_code
domain: 通知验证码短链与消息
status: published
aliases: [verifyCode, indentifyCode, smsCode, 短信验证码, IdentifCode]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: MessageContext.verifyCode + params中的smsCode/timeLimit
field_targets: [MessageContext.verifyCode, params.smsCode, params.timeLimit]
adjudication: synonym
also_confused_with: [checkVerifyCode（校验验证码动作）, sendVerifyCode（发送验证码动作）, IndentifycodeFacade.getIndentifyCode（获取验证码值）]
scope:
  databases: [lowcode_pplatform]
---

“验证码”在消息上下文中统一用 `verifyCode` 或 `smsCode` 承载，由 `indentifycodeFacade.generate` 生成。需区分验证码值与发送/校验动作。

## 需求背景

发送验证码场景包含批量签约、找回密码、注册等。相关规则包括 [[verify_code_send_required_params_validation]]、[[verify_code_validity_config_required]]、[[contract_sign_verify_code_multi_limit]] 等。文档 claim“发送验证码场景集合包含批量签约、找回密码、注册等”已确认。

## 版本演进

基于语义分析 term_bridges 形成 v0.1 契约。短信幂等 RedisSmsLock 使用未在给定代码中完整展示，语义不确定，待 REVIEW。

（无 ground 块，符合 concept 规范）