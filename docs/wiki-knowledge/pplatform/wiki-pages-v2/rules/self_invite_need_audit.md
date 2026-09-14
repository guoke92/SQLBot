---
type: rule
title: 自主/邀请认证需运营中台审核
page_key: self_invite_need_audit
domain: 企业建档与认证
status: draft
aliases:
  - 认证需运营中台审批
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:submitCust
contract_version: "0.1"
belong: rules
---

认证方式为 `SELF`/`INVITE`/`INVITE_AGW` 时，提交后进入 `CUST_CONFIRM_AWAIT` 或 `CUST_BUILDING` 并推送运营中台审核；只有简易认证路径无需审批。该规则决定是否发起运营中台审批。

```ground:rule
name: 自主/邀请认证需运营中台审核
content: identify_style=SELF/INVITE/INVITE_AGW 提交后进入 CUST_CONFIRM_AWAIT/CUST_BUILDING 并推送运营中台审核；仅简易认证无需审批
impact: 决定是否发起运营中台审批
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.identify_style
evidence: code_path:CustCompanyInfoApplication.java:submitCust
```

## 需求背景

认证方式区分了"客户自证"与"平台轻量录入"两类场景（见 [[concepts/identify_style]]），邀请/自主路径需要运营中台把关（对应审核状态字段 `check_status`），简易路径则以客户确认为准。审批状态推进见 [[processes/cust_build_status_state_machine]]。

## 版本演进

v0 初稿：规则以 `submitCust` 的分支写值点固化。运营中台侧回推消息的处理见 `messageNotify`。

关联：[[concepts/cust_building]]、[[concepts/cust_confirm_await]]、[[rules/finance_simple_direct_effect]]。