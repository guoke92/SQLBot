---
type: rule
title: 查询AMS企业联系人列表（产融调用AMS）
page_key: rules/reqdoc-ams-query-contacts
domain: AMS联系人第三方对接
status: published
aliases: [查询AMS联系人]
oid: 1
sources:
  - code
  - reqdoc
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

查询 AMS 企业联系人列表，产融调用 AMS 接口，代码证据为 AmsContactProvider.queryAmsContacts。

## 需求背景
产融平台需要查询 AMS 侧企业联系人列表，需求文档与代码实现一致。

## 版本演进
初始版本为需求文档主张，已由代码证据确认。

```ground:rule
name: "查询AMS企业联系人列表（产融调用AMS）"
content: "查询AMS企业联系人列表（产融调用AMS）"
impact: ""
field_targets: []
evidence: "code_path:AmsContactProvider.queryAmsContacts + reqdoc:查询AMS企业联系人列表（产融调用AMS）"
code_status: confirmed
action: anchor
```

[[enterprise_contact]] [[cust_person_info_do]]