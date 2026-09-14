---
type: caliber
title: 用户未冻结
page_key: user_not_frozen
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 未冻结用户
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserFacade.java:updateListFreezeFlag
contract_version: "0.1"
belong: calibers
---

口径“用户未冻结”：用户列表/角色查询过滤 [[sys_cust_user_rel.is_freeze]] = 'N' 的记录。

## 需求背景

冻结用户不应出现在用户列表与角色授权结果中；冻结状态本身由 SSO 与本地双写维护
（[[freeze_active_dual_write]]、[[sys_cust_user_rel_freeze_state]]）。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 用户未冻结
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 用户列表/角色查询过滤未冻结
evidence: "code_path:UserFacade.java:updateListFreezeFlag"
```

相关：[[sys_cust_user_rel]]、[[sys_cust_user_rel_freeze_state]]、[[login_user_status_state]]。