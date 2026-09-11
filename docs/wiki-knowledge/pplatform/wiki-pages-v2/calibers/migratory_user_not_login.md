---
type: caliber
title: 未登录的迁移用户
page_key: migratory_user_not_login
domain: 租户迁移
status: draft
aliases: [未登录迁移用户口径, 待弹窗迁移用户]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:CustMigratoryService.java:loginAfterEjectMsg
contract_version: "0.1"
---

“未登录的迁移用户”是登录后弹出升级消息这一动作的判定集合：只有同时满足“迁移记录标记为未登录”和“记录有效”的用户才会被纳入。

```ground:caliber
name: 未登录的迁移用户
predicate: "migratory_user_record.is_login = 'N' AND migratory_user_record.enable = 'Y'"
scope: 迁移用户登录弹出消息判断
evidence: "code:CustMigratoryService.loginAfterEjectMsg"
```

## 需求背景

该口径服务于用户触达类需求，落地为 [[eject_msg_once]] 规则的前置条件，并与 [[migratory_user_login_state]] 的 N 态一一对应。语料中未出现与该口径同名的其他写法，暂不设置消歧条目。

## 版本演进

- v0（草稿）：口径由代码证据（`CustMigratoryService.loginAfterEjectMsg`）直接给出，尚无数据侧统计量。

关联页面：[[migratory_user_record]]、[[processes/migratory_user_login_state]]、[[eject_msg_once]]。