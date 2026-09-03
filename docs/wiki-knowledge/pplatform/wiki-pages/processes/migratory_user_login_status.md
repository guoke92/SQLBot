---
type: process
title: 迁移用户登录状态
page_key: migratory_user_login_status
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["db_dist", "code"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 迁移用户登录状态

业务定位：描述存量迁移用户从“未登录”到“已登录”的状态变化，驱动一次性升级弹窗提示。

## 需求背景

存量迁移用户在首次登录新平台前，`migratory_user_record.is_login` 为 `N`。登录成功后系统触发弹窗并将该字段更新为 `Y`，后续登录不再提示。此状态机用于控制一次性提示逻辑。

## 版本演进

暂无。

```ground:process
name: 迁移用户登录状态
field: is_login
states:
  - value: N
    label: 未登录
    source: db_dist
  - value: Y
    label: 已登录
    source: db_dist
transitions:
  - from: N
    event: 存量迁移用户首次登录
    to: Y
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustMigratoryService.java:loginAfterEjectMsg
```