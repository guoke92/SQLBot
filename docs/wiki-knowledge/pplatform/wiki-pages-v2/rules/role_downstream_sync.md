---
type: rule
title: 角色同步下游规则
page_key: role_downstream_sync
domain: 客户角色与端口
status: draft
aliases:
  - roleClass 解析规则
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:RoleFacade.java:generateRoleClass
  - code_path:ClientCustRoleSyncService.java:setInvokeArg
contract_version: "0.1"
belong: rules
---

该规则定义客户角色同步到下游时角色标识的编码/解析约定，涉及 [[company_role]] 术语在跨系统报文中的表达。

## 需求背景

SysRole 的 roleClass 按 "custType_custId" 格式生成，同步下游时再解析出 companyType 与 companyId，因此 roleClass 是客户角色信息在下游侧的复合键载体（影响角色事件同步 PlatClientRoleDto）。

## 版本演进

- v0（draft）：依据 RoleFacade 与 ClientCustRoleSyncService 代码路径成页；下游侧落库表未在证据范围内。

```ground:rule
name: 角色同步下游规则
content: "SysRole 的 roleClass 按 \"custType_custId\" 格式生成，同步下游时解析出 companyType 和 companyId。"
impact: 影响角色事件同步（PlatClientRoleDto）
field_targets:
  - SysRoleDO.roleClass
evidence: "code_path:RoleFacade.java:generateRoleClass, ClientCustRoleSyncService.java:setInvokeArg"
```