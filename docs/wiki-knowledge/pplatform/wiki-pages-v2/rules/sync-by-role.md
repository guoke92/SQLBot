---
type: rule
title: 按角色维度同步
page_key: rules/sync-by-role
domain: 平台事件监听与同步
status: draft
aliases:
  - syncByRole
  - syncByRoleOn
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncService.java:getRoles/syncByRole
contract_version: "0.1"
---

同步维度规则：同步前按 `dbTenantCode + companyCode + (companyType)` 查有效 CustRoleInfoDO，逐角色调用 custClientSyncService；`syncByRoleOn` 开关决定是否忽略 companyType 做全角色同步。

## 需求背景
企业在不同角色下（如 SUPPLIER）对下游系统的可见性不同，因此一次企业事件需要展开为多条按角色同步的 RPC。取数口径见 [[calibers/valid-cust-role]]，角色来源见 [[tables/cust_role_info]]；每条同步 RPC 失败即落 [[tables/client_api_sync_error]]。

## 版本演进
- v0 契约：开关名为 `syncByRoleOn`，默认行为未在语义分析中给出，需配置面确认。

```ground:rule
name: 按角色维度同步
content: "同步前按 dbTenantCode+companyCode+(companyType) 查有效 CustRoleInfoDO，逐角色调用 custClientSyncService；syncByRoleOn 开关决定是否忽略 companyType 全角色同步"
impact: 控制一次企业事件产生多条按角色同步的RPC
field_targets:
  - cust_role_info.role_type
  - cust_role_info.enable
evidence: "CustSyncService.java:getRoles/syncByRole"
related_pages:
  - tables/cust_role_info
  - calibers/valid-cust-role
  - tables/client_api_sync_error
```