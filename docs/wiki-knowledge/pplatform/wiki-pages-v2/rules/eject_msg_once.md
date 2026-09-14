---
type: rule
title: 迁移用户登录后仅弹出一次升级消息
page_key: eject_msg_once
domain: 租户迁移
status: draft
aliases: [升级消息仅弹一次, isEjectMsg 规则]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:CustMigratoryService.java:loginAfterEjectMsg
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
contract_version: "0.1"
belong: rules
---

本规则决定存量用户登录时的触达行为：命中“未登录的迁移用户”后返回弹出标志，并立刻把登录状态置为已登录，从而保证一个用户只被弹一次。

```ground:rule
name: 迁移用户登录后仅弹出一次升级消息
content: 迁移用户（存在于 migratory_user_record 且 is_login='N'）登录后，调用 /cust-web/migratory/isEjectMsg 接口，返回弹出标志，并将 is_login 更新为 'Y'，确保仅弹出一次。
impact: 用户触达
field_targets:
  - migratory_user_record.is_login
evidence: "code_path:CustMigratoryService.java:loginAfterEjectMsg + reqdoc:产融平台数据迁移涉及的改造需求V1.2"
```

## 需求背景

需求文档《产融平台数据迁移涉及的改造需求V1.2》的锚定主张为：登录后弹出提示“【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务。”（通过公告配置实现即可，一个用户仅弹出一次即可）。该主张 code_status=confirmed，与代码证据 `CustMigratoryService.java:loginAfterEjectMsg` 指向同一动作，故按双源写入锚点块。前置集合定义见 [[migratory_user_not_login]]，状态流转见 [[migratory_user_login_state]]。

## 版本演进

- v0（草稿）：规则以代码加需求文档双源固定；提示文案的具体渲染归公告配置，不在本规则内建模。

关联页面：[[migratory_user_record]]、[[migratory_user_login_state]]、[[existing_user]]。