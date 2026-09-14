---
type: concept
title: 永久短链
page_key: permanent_short_link
domain: notification
status: draft
aliases: [永久有效短链, isForever=Y]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
  - db:short_link.is_forever
maps_to: short_link.is_forever = 'Y'
field_targets:
  - short_link.is_forever
  - short_link.expire_time
adjudication: boundary
also_confused_with:
  - temporary_short_link
contract_version: "0.1"
belong: concepts
sources: ["enrich:wiki-admin"]
---

永久短链指 is_forever='Y' 的短链，业务上不设投放截止时间。判定边界：is_forever='Y' 时完全不校验 expire_time；'N' 时校验。与 [[temporary_short_link]] 互为边界，两者与类型维度（[[normal_short_link]] / [[file_short_link]]）正交。

## 需求背景
长期投放的短链（印刷物料、长期协议入口）不能因时间流逝而失效，需求侧要求显式的永久语义。

## 版本演进
- DB 中全部短链当前均为该状态，实际等价于「当前线上默认形态」。
- 状态机见 [[short_link_expire_state]]，口径页见 [[permanent_short_link_skip_expire]]。

相关：[[short_link]]
