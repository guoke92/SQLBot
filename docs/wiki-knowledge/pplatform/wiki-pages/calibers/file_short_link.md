---
type: caliber
title: 文件短链接
page_key: file_short_link
domain: 通知验证码短链与消息
status: published
aliases: [文件短链]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [short_link.type]
scope:
  databases: [lowcode_pplatform]
---

文件短链接口径定义：`short_link.type = 'FILE'`，用于短链类型筛选。文件短链访问时 `source_url` 需解密。

## 需求背景

短链类型为 FILE 时，访问流程需解密源路径。相关规则 [[file_short_link_source_path_decrypt]]，状态机 [[short_link_type]]，表 [[short_link]]。

## 版本演进

本页基于 code_path:ShortLinkController.skipRedirect + db_dist:short_link.type 证据形成 v0.1 契约。

```ground:caliber
name: 文件短链接
predicate: short_link.type = 'FILE'
scope: 短链类型筛选
evidence: code_path:ShortLinkController.skipRedirect + db_dist:short_link.type
```