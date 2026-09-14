---
type: caliber
title: 文件短链加密后跳转
page_key: file_short_link_encrypt_redirect
domain: notification
status: draft
aliases: [FILE 跳转口径, 文件短链加密]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:55
  - db:short_link.type
contract_version: "0.1"
belong: calibers
---

type='FILE' 的短链在跳转前必须先用 filePathEncrypt(source_url,false) 处理 source_url，再重定向，避免真实文件路径暴露。术语定义见 [[file_short_link]]，对应规则见 [[short_link_type_route]]。

## 需求背景
文件类链接的存储路径属于敏感信息，需求侧要求短链对外只暴露短链码，真实路径需加密后跳转。

## 版本演进
- DB 中 FILE 值分布为 605，为短链的次要形态。

```ground:caliber
name: 文件短链加密后跳转
predicate: short_link.type = 'FILE'
scope: 短链访问跳转
evidence: ShortLinkController.java:55 + db
```