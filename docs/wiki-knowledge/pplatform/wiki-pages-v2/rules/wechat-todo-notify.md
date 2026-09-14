---
type: rule
title: 企微待办通知按节点与通知类型分发
page_key: wechat-todo-notify
domain: 企业变更与运营变更
status: draft
aliases: [dispatchWechatNotify, 企微待办, 后补合作协议流程通知]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:BackAgreementProcessOperateListener.java:notice
  - code_path:BackAgreementProcessOperateListener.java:dispatchWechatNotify
contract_version: "0.1"
belong: rules
---

后补合作协议流程仅在 `taskNoticeType=2`（待办通知）时向 `taskNoticeUsers` 反查企微 `userId` 并发送 textcard 待办；其它通知类型忽略。反查不到企微用户时静默返回。

## 需求背景

流程审批待办需要触达到运营人员的企微账号，而流程侧只持有平台用户标识，因此需要一次反查；为避免非待办类通知打扰，仅对待办通知类型发送。该规则涉及 `sys_wx_user.user_id`、`tenant_project_approval.id`，与变更单链路无直接状态耦合，归属本域的外围通知能力。

## 版本演进

v0.1：首次登记，规则来自 `BackAgreementProcessOperateListener.notice` / `dispatchWechatNotify`。

```ground:rule
name: 企微待办通知按节点与通知类型分发
content: 后补合作协议流程仅在 taskNoticeType=2（待办通知）时向 taskNoticeUsers 反查企微 userId 并发送 textcard 待办；其它通知类型忽略
impact: 运营审批待办的企微触达；反查不到企微用户时静默返回
field_targets:
  - sys_wx_user.user_id
  - tenant_project_approval.id
evidence: code_path:BackAgreementProcessOperateListener.java:notice / dispatchWechatNotify
```