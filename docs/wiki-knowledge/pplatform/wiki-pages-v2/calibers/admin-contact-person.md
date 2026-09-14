---
type: caliber
title: 管理员联系人
page_key: admin-contact-person
domain: 平台事件监听与同步
status: draft
aliases:
  - userType=accountAdmin 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
belong: calibers
---

管理员联系人口径：在 [[calibers/valid-contact-person]] 基础上叠加 `user_type='accountAdmin'`，用于按角色取管理员做同步与待办。

## 需求背景
同一手机号可能同时是经办人与管理员，两类身份在权限与同步目标上不同；取管理员时必须显式限定 `user_type='accountAdmin'`，否则会误取经办人。删除场景的对称约束见 [[rules/operator-delete-freeze-only]]。

## 版本演进
- v0.2：口径取自代码层同步实现；`user_type` 取值域为 UserTypeEnum dictKey（accountAdmin/accountNormal/accountGuest）。

```ground:caliber
name: 管理员联系人
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.user_type = 'accountAdmin'"
scope: 按角色取管理员用于同步/待办
evidence: code
related_pages:
  - tables/cust_person_info
  - calibers/valid-contact-person
  - rules/operator-delete-freeze-only
```