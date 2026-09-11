---
type: rule
title: 运营人员分配前提
page_key: rule.operator_assignment_prerequisite
domain: 客户联系人管理
status: draft
aliases:
  - 邀请码发送前置条件
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonController.sendHaveInvitationCode"
  - "code:CustPersonController.sendOperationQrCode"
contract_version: "0.1"
---

向企业发送邀请码或客服名片前，必须先为企业管理员分配运营人员（`operator_id` 不为空）。

## 需求背景

平台为企业指定运营人员作为对接人后，才能以「谁对接谁发送」的方式发出邀请码或客服名片，因此 `operator_id` 为空会阻断发送。相关地，需求文档主张「邀请经办人时发送邀请短信」（code_path:CustPersonApplication.java:sendHaveInvitationCodeForInviteToSign + reqdoc:邀请经办人时发送邀请短信），即邀请经办人时会触发短信通知；经办人接受邀请后以 [[processes/person-account-status]] 的 `ADD`（待激活/新增）进入系统。运营人员字段与企业管理员的关系见 [[concepts/admin]]、[[concepts/handler]]。

```ground:rule
rule: 运营人员分配前提
content: 向企业发送邀请码或客服名片前，必须先为企业管理员分配运营人员（operator_id不为空）
impact: 控制邀请和客服名片发送的前置条件
field_targets:
  - cust_person_info.operator_id
evidence: "code:CustPersonController.sendHaveInvitationCode + code:CustPersonController.sendOperationQrCode + code_path:CustPersonApplication.java:sendHaveInvitationCodeForInviteToSign + reqdoc:邀请经办人时发送邀请短信"
```

## 版本演进

- v0：首次登记。
- （document_claim，未证实）文档主张「邀请码 8 位，30 天有效」在代码中未找到对应实现（code_status=uncovered），见 REVIEW 块。

相关：[[tables/cust_person_info]]、[[concepts/admin]]、[[concepts/handler]]、[[processes/person-account-status]]。