---
type: caliber
title: 普通短链直接跳转
page_key: normal_short_link_redirect
domain: notification
status: draft
aliases: [NORMAL 跳转口径]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:52
contract_version: "0.1"
belong: calibers
---

type='NORMAL' 的短链直接使用 source_url 重定向，不经过文件服务。该口径与 [[file_short_link_encrypt_redirect]] 互斥，术语定义见 [[normal_short_link]]。

## 需求背景
普通短链指向的是页面或外部系统地址，本就可公开，直接重定向可减少一次文件服务调用。

## 版本演进
- DB 中 NORMAL 值分布为 4750，是当前短链的主流形态。

```ground:caliber
name: 普通短链直接跳转
predicate: short_link.type = 'NORMAL'
scope: 短链访问跳转
evidence: ShortLinkController.java:52
```