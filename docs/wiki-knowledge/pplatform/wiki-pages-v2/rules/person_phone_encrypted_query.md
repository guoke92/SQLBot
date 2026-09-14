---
type: rule
title: 联系人手机号加密存储，查询需传密文
page_key: person_phone_encrypted_query
domain: 平台内部服务对接
status: draft
aliases:
  - 手机号密文查询
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.phone]
contract_version: "0.1"
belong: rules
---

cust_person_info.phone 以密文落库（metaDataEncryptionService.encryptAndBase64Str），按手机号检索时必须传入加密后的密文，明文匹配不会命中。

## 需求背景

这是联系人查询（含按手机号定位经办人）的前置条件，属于内部服务对接中的敏感字段处理约定。

## 版本演进

v0：首次成页。

```ground:rule
name: 联系人手机号加密存储，查询需传密文
field: cust_person_info.phone
condition: "按手机号查询联系人"
effect: "查询需传密文（encryptAndBase64Str）"
evidence: code
```