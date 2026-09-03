---
type: rule
title: 迁移用户首次登录弹窗
page_key: migratory_user_first_login_popup
domain: 租户迁移
status: published
aliases: []
oid: 24
sources: [code, reqdoc]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：保证平台升级消息仅首次弹出。

## 需求背景
需求侧确认：迁移客户登录后弹出平台升级提示。代码：CustMigratoryService.java:31-36。

## 版本演进
v0.1 基于代码与需求双源。



关联：[[migratory_user_record_is_login]] [[migratory_user_record]]