---
type: caliber
title: 企微有效成员
page_key: caliber/wecom_active_member
domain: 微信生态/小程序/扫脸
status: draft
aliases: [企微有效成员, 通讯录有效成员]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:WechatContactService.java
contract_version: "0.1"
---

# 企微有效成员

企业微信通讯录的成员有效性口径：status 为空或等于 MEMBER_STATUS_ACTIVATED。用于全量拉取通讯录时的成员过滤。

## 需求背景

企微消息触达对象须为激活成员，避免向停用 / 未激活成员推送。

## 版本演进

v0.1 记录成员过滤谓词。

```ground:caliber
name: 企微有效成员
predicate: "wx_work_user.status IS NULL OR wx_work_user.status = MEMBER_STATUS_ACTIVATED"
scope: "WechatContactService.pullContactList 全量拉取通讯录时过滤停用/未激活成员。"
evidence: code_path:WechatContactService.java#isActiveMember
```

相关：[[wx_work_user]]、[[wechat]]。