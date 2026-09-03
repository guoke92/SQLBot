---
type: rule
title: 迁移用户首登弹窗
page_key: migratory_user_login_popup
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

# 迁移用户首登弹窗

业务定位：控制存量迁移用户首次登录后的升级弹窗提示，确保只提示一次。

## 需求背景

当存量迁移用户 `is_login=N` 且存在记录时，登录后系统返回升级弹窗，并将 `is_login` 更新为 `Y`。该规则与状态机 [[migratory_user_login_status]] 直接关联。

## 版本演进

暂无。

```ground:rule
name: 迁移用户首登弹窗
content: 存量迁移用户 is_login=N 且存在记录，登录后返回升级弹窗并更新 is_login=Y
impact: 一次性提示平台升级，控制重复弹窗
field_targets:
  - migratory_user_record.is_login
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustMigratoryService.java:loginAfterEjectMsg
```

相关：[[migratory_user_record]]
