---
type: concept
title: 企微人员
page_key: wechat_contact_user
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 企微通讯录
  - WechatUserDTO
  - 审批人下拉
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:企微人员"
contract_version: "0.1"
maps_to: tenant_project_approval_flow.approver_user_id
field_targets:
  - tenant_project_approval_flow.approver_user_id
adjudication: boundary
also_confused_with:
  - sys_user.id
belong: concepts
field_targets: [tenant_project_approval_flow.approver_user_id]
sources: ["enrich:wiki-admin"]
---

# 企微人员

## 业务定位

项目审批流中的审批人下拉选项来自企业微信通讯录，落库值为 `tenant_project_approval_flow.approver_user_id`，即企微 userId。

## 需求背景

审批人必须是企微通讯录中真实存在的成员，选择时经 `WechatContactFacade.existsUser` 校验；若误用平台账号体系 id，会出现审批消息下发失败。

## 版本演进

从语义桥证据可见，该字段与平台用户体系是两套标识，未发现二者互转的落库证据。

## 边界

- `approver_user_id` 是企微 userId，需经企微通讯录校验。
- 不是平台 `sys_user.id`。
- 相关消息下发链路见 [[concepts/wechat_message|企微消息]]。

---REVIEW: concept | 企微人员---
语义分析仅给出术语桥，未给出 `tenant_project_approval_flow` 的字段清单与 DDL 证据，本页只登记术语映射与边界；`WechatContactFacade.existsUser` 的具体类路径待补证后写入 sources。
---END REVIEW---

相关：[[tenant_project_approval_flow]]
