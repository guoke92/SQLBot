---
type: rule
title: 内部同步AMS联系人绕过Web上下文
page_key: rule_internal_sync_ams_contact
domain: customer
status: published
aliases: []
oid: 1
sources: []
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则定义内部Dubbo接口同步AMS联系人的方式，不依赖Web上下文。

## 需求背景

`syncContacts` 为内部Dubbo接口，直接调用 `custPersonApplication.contactSync`，不依赖Web上下文，供内部事件触发同步使用。

## 版本演进

规则来自代码路径 `PlatFormAmsProviderImpl.syncContacts`，无文档声明冲突。

```ground:rule
name: 内部同步AMS联系人绕过Web上下文
content: "syncContacts为内部Dubbo接口，直接调用custPersonApplication.contactSync，不依赖Web上下文"
impact: 供内部事件触发同步使用
field_targets:
  - "cust_person_info"
evidence: "code_path:PlatFormAmsProviderImpl.syncContacts"
```