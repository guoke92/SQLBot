---
type: rule
title: 联系人手机号加密后 Base64 存储
page_key: rule.phone_encrypted_base64
domain: 数据权限与组织
status: draft
aliases: [手机号加密, encryptAndBase64Str, decryptStr]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

[[tables/cust_person_info]].phone 不以明文存储：写入时用 encryptAndBase64Str 加密并转 Base64，展示时用 decryptStr 解密。因此库内直接比对手机号字符串不会命中，任何按手机号的查询/去重都必须先走加密链路。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 phone 字段语义（「加密后以 Base64 存储」）得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 手机号加密存储
statement: cust_person_info.phone 加密后以 Base64 存储
condition: 写入或展示手机号
action: 写入用 encryptAndBase64Str，展示用 decryptStr；禁止明文比对
evidence: code_path:cust_person_info.phone（写入用 encryptAndBase64Str，展示用 decryptStr）
```