---
type: concept
title: 游客
page_key: concept.guest
domain: 客户联系人管理
status: draft
aliases:
  - accountGuest
  - guest
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.pagePerson"
maps_to: "cust_person_info.user_type = 'accountGuest'"
adjudication: boundary
also_confused_with:
  - 经办人
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

游客是 [[tables/cust_person_info]] 中 `user_type = 'accountGuest'` 的临时角色记录，取数口径见 [[calibers/person-guest]]。

## 需求背景

游客通常用于企业变更过程中预生成的记录，用于先把人员信息落库，待流程确认后再转为正式角色；因此游客记录往往是暂态数据。

## 边界

游客权限低于经办人（[[concepts/handler]]），不能等同于经办人；两者的区分依据是 `user_type` 值，而不是是否参与业务流程。

## 版本演进

- v0：首次登记，adjudication 为 boundary。

相关：[[calibers/person-guest]]、[[concepts/handler]]、[[concepts/contact-person]]、[[tables/cust_person_info]]。

相关：[[cust_person_info]]
