---
type: caliber
title: 有效联系人
page_key: valid-contact-person
domain: 平台事件监听与同步
status: draft
aliases:
  - enable='Y' 联系人
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustPersonApplication.java:insertOrUpdatePerson
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
belong: calibers
---

有效联系人口径：[[tables/cust_person_info]] 中 `enable='Y'` 的联系人，为同步与查询经办人/管理员时的默认过滤条件。

## 需求背景
联系人被删除或冻结时置 `enable='N'`，因此有效态是同步（SSO/AMS 账号联动）与查询的公共前置条件；在此之上按 `userType` 再细分（[[calibers/admin-contact-person]]）。人维度的 enable 与关联维度的冻结位（[[calibers/operator-role-rel-not-frozen]]）构成两级开关。

## 版本演进
- v0 契约：口径取自代码层同步/查询实现，无 DB 实测。

```ground:caliber
name: 有效联系人
predicate: "cust_person_info.enable = 'Y'"
scope: 同步/查询经办人与管理员时默认过滤
evidence: code
related_pages:
  - tables/cust_person_info
  - calibers/admin-contact-person
  - rules/operator-delete-freeze-only
```