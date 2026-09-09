---
type: rule
title: 文件类型短链接源路径解密
page_key: file_short_link_source_path_decrypt
belong: rules
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [short_link.source_url, short_link.type]
scope:
  databases: [lowcode_pplatform]
---

本规则约束文件类型短链访问：`type='FILE'` 时 `sourceUrl` 需通过 `fileService.getDefaultFileService().filePathEncrypt(link.getSourceUrl(), false)` 解密后重定向，确保文件链接安全访问。

## 需求背景

短链类型 FILE 表示文件链接，源地址加密存储，访问时需解密。相关状态机 [[short_link_type]]、口径 [[file_short_link]]、表 [[short_link]]。

## 版本演进

基于 code_path:ShortLinkController.orderCategory / shortLink 证据形成 v0.1 契约。

```ground:rule
name: 文件类型短链接源路径解密
content: type='FILE'时sourceUrl需通过fileService.getDefaultFileService().filePathEncrypt(link.getSourceUrl(),false)解密后重定向
impact: 文件链接的安全访问
field_targets: [short_link.type, short_link.source_url]
evidence: code_path:ShortLinkController.orderCategory / shortLink
```