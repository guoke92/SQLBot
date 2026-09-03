---
type: caliber
title: 迁移用户未登录
page_key: user_not_login
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [migratory_user_record.is_login]
scope:
  databases: [lowcode_pplatform]
---

# 迁移用户未登录

业务定位：用于识别存量迁移用户在登录弹窗前处于未登录状态的口径。

## 需求背景

该口径基于 `migratory_user_record.is_login = 'N'` 判断用户是否仍需接收升级弹窗。在登录成功后，系统会根据此条件决定是否触发一次性提示。

## 版本演进

暂无。

```ground:caliber
name: 迁移用户未登录
predicate: migratory_user_record.is_login = 'N'
scope: 存量迁移用户首次登录弹窗判断
evidence: code:CustMigratoryService.loginAfterEjectMsg
```

相关：[[migratory_user_record]]
