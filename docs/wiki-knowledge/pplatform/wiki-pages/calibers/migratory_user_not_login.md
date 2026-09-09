---
type: caliber
title: 存量迁移用户未登录口径
page_key: migratory_user_not_login
belong: calibers
domain: 租户迁移
status: published
aliases: [存量迁移用户未登录]
oid: 11
sources: [db]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：筛选未登录的存量迁移用户，用于判断登录后是否弹升级提示。

## 需求背景
迁移客户登录后弹出平台升级提示，需要先识别未登录用户。

## 版本演进
v0.1 基于 DB 字段谓词。

```ground:caliber
name: 存量迁移用户未登录口径
predicate: migratory_user_record.is_login = 'N'
scope: 登录后是否弹升级提示
evidence: db
```

关联：[[migratory_user_record_is_login]] [[migratory_user_record]]