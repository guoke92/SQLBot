---
type: process
title: 迁移用户登录状态（is_login N→Y）
page_key: migratory_user_login_state
domain: 租户迁移
status: draft
aliases: [迁移用户登录状态机, is_login 状态流转]
oid: 1
scope:
  databases: [未提供]
sources:
  - db_dist
  - code_path:CustMigratoryService.java:loginAfterEjectMsg
contract_version: "0.1"
---

本页描述迁移用户的登录状态流转：迁移用户在 [[migratory_user_record]] 中以 `is_login` 标记是否已经过“登录后弹出升级消息”这一动作。状态只有两个取值，迁移客户时记录被初始化为未登录，用户登录并触发弹出接口后翻转为已登录，从而在数据层面实现“仅弹一次”。

```ground:process
name: 迁移用户登录状态
field: migratory_user_record.is_login
states:
  - value: "N"
    label: 未登录
    source: db_dist
  - value: "Y"
    label: 已登录
    source: db_dist
transitions:
  - from: "N"
    event: 用户登录后调用 /cust-web/migratory/isEjectMsg
    to: "Y"
    evidence: "code_path:CustMigratoryService.java:loginAfterEjectMsg"
```

## 需求背景

流转的入口条件是“未登录且有效”的迁移用户，判定口径见 [[migratory_user_not_login]]；翻转动作对应的业务规则（弹出一次升级消息）见 [[eject_msg_once]]。需求文档《产融平台数据迁移涉及的改造需求V1.2》中的锚定主张——“登录后弹出提示‘【贴牌名称】平台已升级，新增【产品中心】……’（通过公告配置实现即可，一个用户仅弹出一次即可）”——与代码证据 `CustMigratoryService.java:loginAfterEjectMsg` 指向同一动作，该主张的双源证据落在 [[eject_msg_once]] 页。

## 版本演进

- v0（草稿）：状态与迁移边来自 db_dist 值分布与 `CustMigratoryService.java:loginAfterEjectMsg`；仅覆盖 N→Y 单向流转，未观察到 Y→N 的回退路径。

关联页面：[[migratory_user_record]]、[[existing_user]]、[[migratory_user_record_init]]。