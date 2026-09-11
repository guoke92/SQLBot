---
type: rule
title: 管理员手机号变更跳转判定
page_key: rule.admin-phone-change-redirect
domain: 企业变更与运营变更
status: draft
aliases: [getRedirectPage, 变更提交成功页跳转]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:getRedirectPage
contract_version: "0.1"
---

变更单含 `UN0012`/`UN0013`（识别口径见 [[calibers.admin-phone-change-item]]）且 `oper_cust_info` 中 `oldPersonId` 与 `personId` 对应手机号不同、且登录手机号 ≠ 新管理员手机号时，跳转变更提交成功页并回填新管理员手机/姓名；否则跳运营中台变更待办页。涉及 [[tables.cust_change_record]]、[[tables.cust_person_info]]，字段边界见 [[concepts.operator]]。

## 需求背景

管理员手机号变更后登录主体发生变化：旧管理员不应再进入变更待办，新管理员则需要看到提交成功结果页。判定必须三方比对（中台旧管理员手机号、中台新管理员手机号、当前登录手机号），避免仅凭变更项就误判。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.getRedirectPage`。

```ground:rule
name: 管理员手机号变更跳转判定
content: 变更单含 UN0012/UN0013 且 oper_cust_info 中 oldPersonId 与 personId 对应手机号不同、且登录手机号≠新管理员手机号时，跳转变更提交成功页并回填新管理员手机/姓名；否则跳运营中台变更待办页
impact: 变更管理员后旧管理员登录不再进入待办，新管理员看到提交成功页
field_targets:
  - cust_change_record.alter_type_id
  - cust_change_record.oper_cust_info
  - cust_person_info.phone
evidence: code_path:CustChangeApplication.java:getRedirectPage
```