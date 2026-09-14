---
type: rule
title: 短链类型路由
page_key: short_link_type_route
domain: notification
status: draft
aliases: [NORMAL 直接跳转, FILE 加密跳转]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:52-55
  - ShortLinkController.java:92-95
contract_version: "0.1"
belong: rules
---

type='NORMAL' 时直接跳转 source_url；type='FILE' 时先 filePathEncrypt(source_url,false) 再跳转。对应口径页 [[normal_short_link_redirect]] 与 [[file_short_link_encrypt_redirect]]。

## 需求背景
文件类短链需要隐藏真实存储路径，需求侧要求文件短链必须走文件服务加密后再重定向。

## 版本演进
- 两个分支当前均有 DB 数据（NORMAL 4750 / FILE 605）。

```ground:rule
name: 短链类型路由
content: type='NORMAL' 直接跳转 source_url；type='FILE' 先 filePathEncrypt(source_url,false) 再跳转
impact: 文件短链需走文件服务加密
field_targets:
  - short_link.type
  - short_link.source_url
evidence: ShortLinkController.java:52-55,92-95
```