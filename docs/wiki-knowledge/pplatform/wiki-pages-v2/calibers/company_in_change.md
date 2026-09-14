---
type: caliber
title: 变更中企业
page_key: company_in_change
domain: 企业变更与运营变更
status: draft
aliases: [变更在途企业, CHANGE 状态口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: calibers
---

口径定义：`cust_company_info.cust_status = 'CHANGE'` 即视为该企业存在变更在途。该口径用于变更待办页与变更提交成功页的跳转判定，也是 [[change_on_way]] 规则的判定依据。

## 需求背景

变更在途的判定以企业主体状态为唯一入口，避免逐条扫描变更记录；跳转分支因此稳定且可缓存。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 变更中企业
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: 变更待办页/变更提交成功页跳转判定
evidence: "code_path:CustChangeApplication.java#getRedirectPage"
```

相关页面：[[cust_company_info]]、[[cust_company_info_cust_status]]、[[change_on_way]]、[[admin_mobile_redirect]]。