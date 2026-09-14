---
type: concept
title: 文件短链
page_key: file_short_link
domain: notification
status: draft
aliases: [FILE 短链]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:55
maps_to: short_link.type = 'FILE'
field_targets:
  - short_link.type
  - short_link.source_url
adjudication: boundary
also_confused_with:
  - normal_short_link
contract_version: "0.1"
belong: concepts
sources: ["enrich:wiki-admin"]
---

文件短链指 type='FILE' 的短链。判定边界：source_url 需经 filePathEncrypt 加密后再重定向，避免暴露真实文件路径。与 [[normal_short_link]] 互为边界。

## 需求背景
文件存储路径属于敏感信息，需求侧要求对外只暴露短链码。

## 版本演进
- DB 值分布 FILE 605。
- 口径页见 [[file_short_link_encrypt_redirect]]，路由规则见 [[short_link_type_route]]。

相关：[[short_link]]
