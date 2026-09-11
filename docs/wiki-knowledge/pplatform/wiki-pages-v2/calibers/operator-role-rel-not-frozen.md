---
type: caliber
title: 经办人角色关联未冻结
page_key: calibers/operator-role-rel-not-frozen
domain: 平台事件监听与同步
status: draft
aliases:
  - is_freeze='N'
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

未冻结口径：[[tables/sys_cust_user_rel]] 中 `is_freeze='N'` 的用户-客户角色关联，用于删除企业时判断该用户是否仍被占用、是否可删。

## 需求背景
删除企业需要判断用户是否可回收：只要还存在未冻结的角色关联，就不能直接删除用户；冻结是回收权限的软手段（[[rules/operator-delete-freeze-only]]）。

## 版本演进
- v0 契约：口径取自代码层删除判定实现，无 DB 实测。

```ground:caliber
name: 经办人角色关联未冻结
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 删除企业时判断是否可删用户
evidence: code
related_pages:
  - tables/sys_cust_user_rel
  - rules/operator-delete-freeze-only
```