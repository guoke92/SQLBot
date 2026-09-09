---
type: process
title: migratory_user_record.is_login
page_key: migratory_user_record_is_login
belong: processes
domain: 租户迁移
status: published
aliases: [迁移用户登录状态]
oid: 5
sources: [db_dist, code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：迁移用户登录状态机，控制平台升级提示是否弹出。

## 需求背景
迁移客户登录后弹出平台升级提示（已证实）。code_path: CustMigratoryService.java:31-36 + reqdoc: 迁移客户登录后弹出平台升级提示。存量迁移用户首次登录后触发弹窗，将 N 置为 Y。

## 版本演进
v0.1 状态与转换基于 DB 分布与代码证据。

```ground:state_machine
field: migratory_user_record.is_login
states:
  - value: N
    label: 未登录
    source: db_dist
  - value: Y
    label: 已登录
    source: db_dist
transitions:
  - from: N
    event: 存量迁移用户首次登录后触发弹窗
    to: Y
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustMigratoryService.java:31-36 + reqdoc:迁移客户登录后弹出平台升级提示"
```

关联：[[migratory_user_first_login_popup]] [[migratory_user_record]]