---
type: caliber
title: 有效客户角色
page_key: calibers/valid-cust-role
domain: 平台事件监听与同步
status: draft
aliases:
  - cust_role_info.enable='Y'
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncService.java:getRoles/syncByRole
contract_version: "0.1"
---

有效客户角色口径：按角色同步时仅取 [[tables/cust_role_info]] 中 `enable='Y'` 的角色作为同步维度。

## 需求背景
一次企业事件会产生多条按角色的同步 RPC，若把停用角色纳入，会造成无效调用与下游脏数据；因此同步前先按 `dbTenantCode + companyCode + (companyType)` 过滤有效角色（[[rules/sync-by-role]]）。

## 版本演进
- v0 契约：口径取自代码层 `CustSyncService.getRoles/syncByRole`，无 DB 实测。

```ground:caliber
name: 有效客户角色
predicate: "cust_role_info.enable = 'Y'"
scope: 按角色同步时取角色维度
evidence: code
related_pages:
  - tables/cust_role_info
  - rules/sync-by-role
```