---
type: caliber
title: 密钥对数2
page_key: key_num_2
domain: 准入接入与接入密钥
status: draft
aliases:
  - key_num=2
  - 密钥对数
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 密钥对数2

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `key_num` 的取值现状：全量样本取值唯一，均为 2，即每个渠道配置两对密钥材料。

## 需求背景

接入密钥支持多对密钥（便于轮换或双活），当前实际配置统一为两对；与 `pub_key` / `pri_key` 文件路径配置配套使用。

## 版本演进

DB 取值为单一值 2，无历史多值证据。

```ground:caliber
name: 密钥对数2
predicate: "cust_access_secret.key_num = '2'"
scope: cust_access_secret全量样本
evidence: "db:key_num distinct=1, 2"
```