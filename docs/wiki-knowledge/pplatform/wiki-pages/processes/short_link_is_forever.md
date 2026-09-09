---
type: process
title: short_link_is_forever
page_key: short_link_is_forever
belong: processes
domain: 通知验证码短链与消息
status: published
aliases: [短链永久有效标识]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [short_link.is_forever]
scope:
  databases: [lowcode_pplatform]
---

short_link_is_forever 是字段 `short_link.is_forever` 的状态机，包含 Y（永久有效）与 N（非永久依赖过期时间）两个状态。它参与有效短链判定。

## 需求背景

短链访问时需判断是否过期：永久短链跳过时间校验，非永久短链需要检查 `expire_time`。相关口径 [[valid_short_link]]，规则 [[short_link_expiration_judgment]]，表 [[short_link]]。

## 版本演进

本页状态基于 db_dist:short_link.is_forever，v0.1 契约不含转移。

```ground:process
name: short_link_is_forever
field: short_link.is_forever
states:
  - value: Y
    label: 永久有效
    source: db_dist
  - value: N
    label: 非永久（依赖过期时间）
    source: db_dist
transitions: []
evidence: db_dist:short_link.is_forever
```