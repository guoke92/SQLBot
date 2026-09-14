---
type: caliber
title: 管理员手机号类变更项
page_key: admin_mobile_change_items
domain: 企业变更与运营变更
status: draft
aliases: [UN0012/UN0013 变更项, 管理员手机号变更项集合]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: calibers
---

口径定义：变更项编码落在 `UN0012`（企业管理员变更）、`UN0013`（管理员手机号变更）的集合，即为触发变更提交成功页跳转判定的变更项，见 [[admin_mobile_redirect]] 与 [[change_item_contains]]。

## 需求背景

只有会改变管理员手机号的变更项才需要提示登录人重新确认身份，因此把这两个编码作为固定集合维护。

## 版本演进

v0.1：首次固化该口径；编码取自 `CustUpdateItemCodeConstants`。

```ground:caliber
name: 管理员手机号类变更项
predicate: "cust_change_cfg.item_code IN ('UN0012','UN0013')"
scope: 触发变更提交成功页跳转的变更项集合
evidence: "code_path:CustChangeApplication.java#getRedirectPage(CustUpdateItemCodeConstants.UN0012/UN0013)"
```

相关页面：[[change_item_code]]、[[change_item_contains]]、[[admin_mobile_redirect]]、[[company_admin_contact]]。