---
type: rule
title: queryMenu 角色转换
page_key: queryMenu 角色转换
domain: 门户侧边栏查询
status: published
aliases: []
oid: 1

sources:
  - code_path:LocalTypeMenuService.listByProductCodeAndCompanyType -> CustCompanyFacade.getAuthRoleCode -> RoleFacade.listMenuByRole
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则说明菜单查询前必须将企业角色 companyType 转换为权限系统授权角色 code，再调用 RoleFacade.listMenuByRole 查询角色菜单。菜单内容由角色权限决定，非租户定制。相关概念 [[companyType]] 与 [[authRoleCode]] 的边界在此体现，口径 [[queryMenu-产品+企业角色菜单]] 依赖此转换。

## 需求背景

权限系统只识别授权角色 code，而业务侧传递的是企业角色编码，因此引入映射层 CustCompanyFacade.getAuthRoleCode 完成转换，确保菜单数据来源于权限系统。

## 版本演进

当前映射逻辑固化在 Facade 中，若权限角色模型升级，需要同步调整 Facade 实现而不影响调用方。

```ground:rule
name: queryMenu 角色转换
content: 通过 CustCompanyFacade.getAuthRoleCode(companyType) 将企业角色转换为授权角色 code，再调用 RoleFacade.listMenuByRole 查询角色菜单
impact: 菜单内容由角色权限决定，非租户定制
field_targets:
  - queryMenu.companyType
  - sys_menu
evidence: code_path:LocalTypeMenuService.listByProductCodeAndCompanyType -> CustCompanyFacade.getAuthRoleCode -> RoleFacade.listMenuByRole
```