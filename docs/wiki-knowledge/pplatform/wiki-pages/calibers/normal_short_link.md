---
type: caliber
title: 普通短链接
page_key: normal_short_link
belong: calibers
domain: 通知验证码短链与消息
status: published
aliases: [普通短链]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [short_link.type]
scope:
  databases: [lowcode_pplatform]
---

普通短链接口径定义：`short_link.type = 'NORMAL'`，用于短链类型筛选。普通短链跳转无需解密。

## 需求背景

短链访问时根据类型分流，普通短链直接重定向。相关状态机 [[short_link_type]]，口径 [[file_short_link]]，表 [[short_link]]。

## 版本演进

本页基于 code_path:ShortLinkController.skipRedirect 证据形成 v0.1 契约。

```ground:caliber
name: 普通短链接
predicate: short_link.type = 'NORMAL'
scope: 短链类型筛选
evidence: code_path:ShortLinkController.skipRedirect
```