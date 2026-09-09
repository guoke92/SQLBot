---
type: rule
title: 短链接过期判定
page_key: short_link_expiration_judgment
belong: rules
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [short_link.expire_time, short_link.is_forever]
scope:
  databases: [lowcode_pplatform]
---

本规则约束短链过期检查：非永久短链（`is_forever='N'`）且当前时间不早于 `expire_time` 时判定过期，抛出“访问的文件链接已过期”，阻止访问。

## 需求背景

短链访问必须基于 [[valid_short_link]] 口径过滤。过期短链无法访问，相关状态机 [[short_link_is_forever]]，表 [[short_link]]。

## 版本演进

基于 code_path:ShortLinkController.orderCategory / shortLink 证据形成 v0.1 契约。

```ground:rule
name: 短链接过期判定
content: 非永久短链（is_forever='N'）且当前时间不早于expire_time时判定过期，抛出“访问的文件链接已过期”
impact: 过期短链无法访问
field_targets: [short_link.is_forever, short_link.expire_time]
evidence: code_path:ShortLinkController.orderCategory / shortLink
```