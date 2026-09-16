---
type: enum
title: identify_style
page_key: identify_style
domain: 企业建档与认证状态机
status: draft
aliases: [认证方式]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:IdentifyTypeConstant.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# identify_style

[[cust_company_info]] 的 `identify_style`：企业如何进入建档。常量注释见 `IdentifyTypeConstant`。从 `INIT` 走出的分叉见 [[cust_build_status_flow]]。

```ground:enum
enum: identify_style
fields: [cust_company_info.identify_style]
values:
  "INVITE":
    label: "邀请认证-客户录入"
  "INVITE_AGW":
    label: "邀请认证-内管录入"
  "SIMPLE":
    label: "简易认证"
  "SELF":
    label: "自主认证"
```
