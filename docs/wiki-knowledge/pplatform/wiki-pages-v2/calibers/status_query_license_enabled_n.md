---
type: caliber
title: 建档状态查询返回营业执照并同步SFTP关闭
page_key: status_query_license_enabled_n
domain: 准入接入与接入密钥
status: draft
aliases:
  - status_query_license_enabled=N
  - 执照同步关闭
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 建档状态查询返回营业执照并同步SFTP关闭

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `status_query_license_enabled = 'N'` 的渠道不返回营业执照、不做 SFTP 同步。DB 中 18 条渠道处于关闭状态，是当前多数渠道的默认配置。

## 需求背景

与开启口径对称，用于按渠道控制执照回传行为；默认关闭可减少不必要的文件同步。

## 版本演进

同 [[calibers/status_query_license_enabled_y|建档状态查询返回营业执照并同步SFTP开启]]，该字段未在给定代码中出现，行为描述待证实。

```ground:caliber
name: 建档状态查询返回营业执照并同步SFTP关闭
predicate: "cust_access_secret.status_query_license_enabled = 'N'"
scope: DB中18条渠道关闭
evidence: "db:status_query_license_enabled N=18"
```