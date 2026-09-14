---
type: caliber
title: 建档状态查询返回营业执照并同步SFTP开启
page_key: status_query_license_enabled_y
domain: 准入接入与接入密钥
status: draft
aliases:
  - status_query_license_enabled=Y
  - 执照同步开启
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 建档状态查询返回营业执照并同步SFTP开启

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `status_query_license_enabled = 'Y'` 时，建档状态查询会返回营业执照并同步 SFTP。DB 中 3 条渠道开启该能力。

## 需求背景

不同渠道对执照回传的要求不同，因此按渠道粒度开关该行为，而不是全局开关。

## 版本演进

该字段在 DB 中存在（Y=3、N=18），但给定代码中 `CustAccessSecretDO` 未定义该字段，接入链路亦未见读取，说明代码侧与库结构可能未同步，属未证实项，需 REVIEW 后再引用。对称口径见 [[calibers/status_query_license_enabled_n|建档状态查询返回营业执照并同步SFTP关闭]]。

```ground:caliber
name: 建档状态查询返回营业执照并同步SFTP开启
predicate: "cust_access_secret.status_query_license_enabled = 'Y'"
scope: DB中3条渠道开启，代码链路未读取该字段，需REVIEW
evidence: "db:status_query_license_enabled Y=3,N=18"
```

---REVIEW: caliber | 建档状态查询返回营业执照并同步SFTP开启
- 代码侧 `CustAccessSecretDO` 未定义该字段，无法确认真实生效路径；「返回营业执照并同步SFTP」的行为描述仅有字段名推证，需代码或需求文档佐证。
---END REVIEW---