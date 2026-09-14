---
type: rule
title: 管理员手机号变更后的页面跳转
page_key: admin_mobile_redirect
domain: 企业变更与运营变更
status: draft
aliases: [getRedirectPage, 变更提交成功页跳转]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: rules
---

规则内容：变更项命中 `UN0012`/`UN0013`（[[admin_mobile_change_items]]）时，解析 `oper_cust_info` 的 `oldPersonId`/`personId` 取新旧管理员手机号（[[before_after_comparison]]、[[company_admin_contact]]）；若新旧手机号不同且与登录手机号不同，跳转变更提交成功页并回带新管理员手机号/姓名，否则跳运营中台变更待办页。

## 需求背景

管理员手机号被改掉后，当前登录人的手机号可能已不是企业管理员手机号，需要引导其确认身份或前往中台待办，避免继续用失效身份操作。

## 版本演进

v0.1：首次固化跳转分支与判定顺序。

```ground:rule
name: 管理员手机号变更后的页面跳转
content: "变更项命中 UN0012/UN0013 时解析 oper_cust_info 的 oldPersonId/personId 取新旧管理员手机号；若新旧手机号不同且与登录手机号不同，跳转变更提交成功页并回带新管理员手机号/姓名，否则跳运营中台变更待办页"
impact: 变更后登录人手机号与管理员不一致时引导重新登录/查看
field_targets:
  - cust_change_record.alter_type_id
  - cust_change_record.oper_cust_info
  - cust_person_info.phone
evidence: "code_path:CustChangeApplication.java#getRedirectPage"
```

相关页面：[[admin_mobile_change_items]]、[[before_after_comparison]]、[[company_admin_contact]]、[[cust_person_info]]、[[valid_change_record]]。