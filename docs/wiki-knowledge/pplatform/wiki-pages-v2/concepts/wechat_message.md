---
type: concept
title: 企微消息
page_key: wechat_message
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 企业微信消息
  - textcard
  - 待办提醒
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:企微消息"
contract_version: "0.1"
maps_to: tenant_project_approval_flow.approver_user_id
field_targets:
  - tenant_project_approval_flow.approver_user_id
adjudication: boundary
also_confused_with:
  - 微信服务号消息
  - DBASS 微信通知 WechatNotificationService
belong: concepts
field_targets: [tenant_project_approval_flow.approver_user_id]
sources: ["enrich:wiki-admin"]
---

# 企微消息

## 业务定位

项目审批待办提醒走企业微信消息通道（`message/send`，textcard 形式），接收方由 `tenant_project_approval_flow.approver_user_id` 决定，见 [[concepts/wechat_contact_user|企微人员]]。

## 需求背景

同一业务存在多条微信触达链路，混用会导致消息发到错误通道或错误接收人，因此需要在术语层明确区分。

## 版本演进

从语义桥证据可见，企微消息直连企业微信接口；服务号通知与 DBASS 的 `IWeiXinApi` / `WechatNotificationService` 属于另一链路。

## 边界

- 企微消息：企业微信应用消息，接收人为企微 userId。
- 微信服务号消息：另一套模板消息链路。
- DBASS 微信通知：`WechatNotificationService` / `IWeiXinApi` 链路，不可与企微消息互换。

---REVIEW: concept | 企微消息---
语义桥未给出企微消息发送实现类路径与消息模板字段，本页只登记术语边界；具体 `message/send` 调用点待补证。
---END REVIEW---

相关：[[tenant_project_approval_flow]]
