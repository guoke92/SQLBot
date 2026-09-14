---
type: caliber
title: 接入密钥加密类型RSA
page_key: encry_type_rsa
domain: 准入接入与接入密钥
status: draft
aliases:
  - encry_type=rsa
  - RSA 密钥类型
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 接入密钥加密类型RSA

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `encry_type` 的取值现状：全量样本的取值唯一，均为 `rsa`。它决定 `pub_key` / `pri_key` 所指向证书文件的加解密方式，是 [[concepts/access_secret|接入密钥]] 配置的一部分。

## 需求背景

接入密钥以文件路径 + 加密类型的方式配置，当前接入方统一使用 RSA，未出现其他加密类型。

## 版本演进

DB 取值为单一值 `rsa`，无历史多值证据；若后续引入国密等其他类型，需重估本口径。

```ground:caliber
name: 接入密钥加密类型RSA
predicate: "cust_access_secret.encry_type = 'rsa'"
scope: cust_access_secret全量样本
evidence: "db:encry_type distinct=1, rsa"
```