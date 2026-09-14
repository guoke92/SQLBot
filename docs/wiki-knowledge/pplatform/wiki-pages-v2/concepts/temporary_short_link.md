---
type: concept
title: 限时短链
page_key: temporary_short_link
domain: notification
status: draft
aliases: [非永久短链, isForever=N]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
maps_to: short_link.is_forever = 'N'
field_targets:
  - short_link.is_forever
  - short_link.expire_time
adjudication: boundary
also_confused_with:
  - permanent_short_link
contract_version: "0.1"
belong: concepts
sources: ["enrich:wiki-admin"]
---

限时短链指 is_forever='N' 的短链，业务上有明确投放截止时间。判定边界：需 expire_time > now，否则视为过期并拦截。与 [[permanent_short_link]] 互为边界。

## 需求背景
活动、临时入口类链接需要到期自动失效，需求侧要求以字段而非人工下架控制。

## 版本演进
- 该状态当前在 DB 中无数据样本，属于代码已实现、数据未启用。
- 口径页见 [[temporary_short_link_expire_check]]，拦截规则见 [[short_link_expire_check]]。

相关：[[short_link]]
