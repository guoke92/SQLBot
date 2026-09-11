---
type: table
title: wx_work_user（企微成员表）
page_key: table/wx_work_user
domain: 微信生态/小程序/扫脸
status: draft
aliases: [企微成员, 企业微信成员表]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:WechatContactService.java
contract_version: "0.1"
---

# wx_work_user

企业微信通讯录成员表。用于企微消息触达时的成员过滤：仅激活成员可被纳入内部审批 / 通知对象。

## 需求背景

`WechatContactService.pullContactList` 全量拉取通讯录时，按成员状态过滤停用 / 未激活成员，避免向无效成员推送消息。

## 版本演进

v0.1 仅记录成员状态过滤口径 [[wecom_active_member]]；成员字段全集待补充。



相关：[[wecom_active_member]]、[[wechat]]。