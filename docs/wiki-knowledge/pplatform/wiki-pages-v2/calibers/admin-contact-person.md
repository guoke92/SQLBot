---
type: caliber
title: 管理员联系人
page_key: calibers/admin-contact-person
domain: 平台事件监听与同步
status: draft
aliases:
  - userType=admin 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

管理员联系人口径：在 [[calibers/valid-contact-person]] 基础上叠加 `user_type='admin'`，用于按角色取管理员做同步与待办。

## 需求背景
同一手机号可能同时是经办人与管理员，两类身份在权限与同步目标上不同；取管理员时必须显式限定 `userType='admin'`，否则会误取经办人。删除场景的对称约束见 [[rules/operator-delete-freeze-only]]。

## 版本演进
- v0 契约：口径取自代码层同步实现；`userType` 取值域为 UserTypeEnum（admin/operator/guest）。

```ground:caliber
name: 管理员联系人
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.user_type = 'admin'"
scope: 按角色取管理员用于同步/待办
evidence: code
related_pages:
  - tables/cust_person_info
  - calibers/valid-contact-person
  - rules/operator-delete-freeze-only
```