---
type: process
title: short_link_type
page_key: short_link_type
domain: 通知验证码短链与消息
status: published
aliases: [短链类型]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [short_link.type]
scope:
  databases: [lowcode_pplatform]
---

short_link_type 是字段 `short_link.type` 的状态机，包含 NORMAL（普通跳转）与 FILE（文件链接）两个状态。它决定短链访问时是否需要对 `source_url` 解密。

## 需求背景

短链访问根据类型分支：NORMAL 直接跳转，FILE 需解密后重定向。相关口径 [[normal_short_link]]、[[file_short_link]]，规则 [[file_short_link_source_path_decrypt]]，表 [[short_link]]。

## 版本演进

本页状态基于 db_dist:short_link.type，v0.1 契约不含转移。

```ground:process
name: short_link_type
field: short_link.type
states:
  - value: NORMAL
    label: 普通跳转
    source: db_dist
  - value: FILE
    label: 文件链接
    source: db_dist
transitions: []
evidence: db_dist:short_link.type
```