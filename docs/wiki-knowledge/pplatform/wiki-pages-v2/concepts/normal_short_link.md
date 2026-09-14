---
type: concept
title: 普通短链
page_key: normal_short_link
domain: notification
status: draft
aliases: [NORMAL 短链]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:52
maps_to: short_link.type = 'NORMAL'
field_targets:
  - short_link.type
  - short_link.source_url
adjudication: boundary
also_confused_with:
  - file_short_link
contract_version: "0.1"
belong: concepts
sources: ["enrich:wiki-admin"]
---

普通短链指 type='NORMAL' 的短链。判定边界：直接使用 source_url 重定向，不做加密处理。与 [[file_short_link]] 互为边界；类型维度与有效期维度（[[permanent_short_link]] / [[temporary_short_link]]）正交。

## 需求背景
指向页面与外部系统的短链本就可公开，需求侧不要求额外隐藏处理。

## 版本演进
- DB 值分布 NORMAL 4750，是短链主要形态。
- 口径页见 [[normal_short_link_redirect]]，路由规则见 [[short_link_type_route]]。

相关：[[short_link]]
