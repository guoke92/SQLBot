---
type: process
title: 短链有效期状态
page_key: short_link_expire_state
domain: notification
status: draft
aliases: [短链有效期状态机, is_forever 状态]
oid: 1
scope:
  databases: []
sources:
  - db:short_link.is_forever
  - ShortLinkController.java:48
contract_version: "0.1"
belong: processes
---

该状态机描述短链按 is_forever 的两态划分：永久有效与限时有效。两个状态对应 [[permanent_short_link]] 与 [[temporary_short_link]]，判定发生在访问跳转链路上，具体口径见 [[permanent_short_link_skip_expire]] 与 [[temporary_short_link_expire_check]]。

## 需求背景
短链的过期语义不应由 expire_time 是否为空隐式表达，需求侧要求显式的到期类型字段，使访问端可以明确区分「永不校验过期」与「必须校验过期」。

## 版本演进
- Y 态有 DB 全量数据支撑；N 态仅有代码常量证据，DB 无样本，转换条件（谁会写入 N、何时写入）在本次分析中无证据。

```ground:process
name: 短链有效期状态
field: short_link.is_forever
states:
  - value: "Y"
    label: 永久有效
    source: db_dist
  - value: "N"
    label: 限时有效
    source: code_const
transitions: []
```