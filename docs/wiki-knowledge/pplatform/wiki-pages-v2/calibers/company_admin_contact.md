---
type: caliber
title: 企业管理员联系人
page_key: company_admin_contact
domain: 企业变更与运营变更
status: draft
aliases: [管理员联系人口径, user_type=admin]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
  - code:CustSyncEventProvider.java
contract_version: "0.1"
belong: calibers
---

口径定义：定位企业管理员时取 [[cust_person_info]] 中 `user_type = 'accountAdmin'` 的联系人。管理员变更、管理员手机号变更（[[admin_mobile_change_items]]）都以此为起点。

## 需求背景

同一企业下联系人类型混杂（管理员、经办人），变更判定必须只针对管理员这一类型，否则会把经办人手机号误判为管理员手机号。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 企业管理员联系人
predicate: "cust_person_info.user_type = 'accountAdmin'"
scope: 管理员变更/手机号变更时定位联系人
evidence: "code_path:CustChangeApplication.java#getRedirectPage + CustSyncEventProvider.java#getAuthChangeCompanyType(UserTypeEnum.admin)"
```

相关页面：[[cust_person_info]]、[[admin_mobile_change_items]]、[[admin_mobile_redirect]]、[[operator]]。