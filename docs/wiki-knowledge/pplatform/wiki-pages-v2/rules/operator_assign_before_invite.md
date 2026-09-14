---
type: rule
title: 发送邀请码/客服名片需先分配运营
page_key: operator_assign_before_invite
domain: 经办人/联系人/管理员管理
status: draft
aliases: [sendHaveInvitationCode, sendOperationQrCode, 分配运营]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonController.java#sendHaveInvitationCode,#sendOperationQrCode + CustPersonApplication.java#getCustomerOperatorQrCode"]
contract_version: "0.1"
belong: rules
---

sendHaveInvitationCode 与 sendOperationQrCode 接口均校验 operator_id 非空，否则提示"请先完成分配运营"；客服名片还要求角色表/企业表能取到 platformCustId 且租户配置了 customer_card_type（[[operator]]、[[cust_person_info]]）。

## 需求背景
- 该规则把运营分配设为邀请码与客服名片的硬前置，运营未分配时相关功能不可用（[[operator]]）。

## 版本演进
- 当前版本客服名片新增了两项额外前置：platformCustId 可获取、租户配置 customer_card_type。

```ground:rule
name: 发送邀请码/客服名片需先分配运营
content: "sendHaveInvitationCode 与 sendOperationQrCode 接口校验 operator_id 非空，否则提示“请先完成分配运营”。客服名片要求角色表/企业表能取到 platformCustId 且租户配置了 customer_card_type"
impact: 运营未分配时业务不可用
field_targets:
  - cust_person_info.operator_id
evidence: "code_path:CustPersonController.java#sendHaveInvitationCode,#sendOperationQrCode + CustPersonApplication.java#getCustomerOperatorQrCode"
```

相关页面：[[cust_person_info]]、[[operator]]、[[batch_change_operator_template]]。