---
type: caliber
title: 有效短链接
page_key: valid_short_link
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

有效短链接口径定义：短链永久有效或未到期时视为有效，用于短链访问跳转场景。该口径是短链过期拦截的核心条件。

## 需求背景

短链访问前需要过滤无效记录，有效性由 `short_link.is_forever` 与 `short_link.expire_time` 组合决定。相关规则 [[short_link_expiration_judgment]]，状态机 [[short_link_is_forever]]，表 [[short_link]]。

## 版本演进

本页基于 code_path:ShortLinkController.orderCategory / shortLink 证据形成 v0.1 契约。

```ground:caliber
name: 有效短链接
predicate: short_link.is_forever = 'Y' OR (short_link.is_forever = 'N' AND short_link.expire_time > NOW())
scope: 短链访问跳转
evidence: code_path:ShortLinkController.orderCategory / shortLink
```