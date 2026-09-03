---
type: concept
title: 短链接
page_key: short_link
domain: 通知验证码短链与消息
status: published
aliases: [短链, short_link, shortLink, sl, ShortLinkDO]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: short_link表（number/source_url/type/is_forever/expire_time）
field_targets: [short_link.number, short_link.source_url, short_link.type, short_link.is_forever, short_link.expire_time]
adjudication: boundary
also_confused_with: [ShortLinkDO.id（短链主键，与number编码不同）, source_url（原始链接，与number短码不同）]
scope:
  databases: [lowcode_pplatform]
---

“短链接”是短链访问能力的核心概念，对应 `short_link` 表记录。访问时通过 `number` 编码或 `id` 定位，最终重定向到 `source_url`。其边界：短链接 = short_link 表记录；访问时通过 number 或 id 编码定位，最终跳转 source_url。

## 需求背景

短链接在通知/消息主题中用于文件下载、跳转等场景。需注意区分主键 `id` 与业务编码 `number`，以及 `number` 与原始 `source_url` 的差异。相关表 [[short_link]]、状态机 [[short_link_type]] / [[short_link_is_forever]]、规则 [[short_link_expiration_judgment]] 等。

## 版本演进

基于语义分析 term_bridges 形成 v0.1 契约。文档声称“需要短链时 ShortLinkAppication 生成短链”在给定代码中未见生成逻辑，标记为待确认。

（无 ground 块，符合 concept 规范）