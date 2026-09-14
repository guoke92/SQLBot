---
type: rule
title: 短链过期校验
page_key: short_link_expire_check
domain: notification
status: draft
aliases: [链接已过期, 短链拦截]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
  - ShortLinkController.java:83
contract_version: "0.1"
belong: rules
---

is_forever='N' 且 expire_time <= now 时抛出链接已过期，短链访问被拦截。对应的口径页为 [[temporary_short_link_expire_check]]，永久短链不受此校验见 [[permanent_short_link_skip_expire]]。

## 需求背景
限时短链到期必须自动失效，需求侧要求访问端直接拦截而不是返回目标地址。

## 版本演进
- 该分支当前无 DB 数据，属于已实现未使用的能力。

```ground:rule
name: 短链过期校验
content: is_forever='N' 且 expire_time <= now 时抛出链接已过期
impact: 短链访问拦截
field_targets:
  - short_link.is_forever
  - short_link.expire_time
evidence: ShortLinkController.java:48,83
```