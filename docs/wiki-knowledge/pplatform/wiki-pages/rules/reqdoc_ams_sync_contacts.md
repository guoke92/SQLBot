---
type: rule
title: 同步AMS联系人到产融（内部Dubbo调用）
page_key: rules/reqdoc-ams-sync-contacts
domain: AMS联系人第三方对接
status: published
aliases: [AMS同步联系人]
oid: 1
sources:
  - code
  - reqdoc
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

同步 AMS 联系人到产融，通过内部 Dubbo 调用 PlatFormAmsProviderImpl.syncContacts 实现。

## 需求背景
AMS 联系人同步至产融平台，需求文档与代码实现一致。

## 版本演进
初始版本为需求文档主张，已由代码证据确认。

```ground:rule
name: "同步AMS联系人到产融（内部Dubbo调用）"
content: "同步AMS联系人到产融（内部Dubbo调用）"
impact: ""
field_targets: []
evidence: "code_path:PlatFormAmsProviderImpl.syncContacts + reqdoc:同步AMS联系人到产融（内部Dubbo调用）"
code_status: confirmed
action: anchor
```

[[enterprise_contact]] [[cust_person_info_do]]