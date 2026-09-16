---
type: enum
title: short_link_type
page_key: short_link_type
domain: 通知/验证码/短链
status: draft
aliases: [文件短链]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# short_link_type

`ShortLinkType`。

```ground:enum
enum: short_link_type
fields:
  - short_link.type
values:
  "FILE":
    label: "文件类型"
  "NORMAL":
    label: "一般类型"
```
