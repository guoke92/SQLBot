---
type: concept
title: authRoleCode
page_key: authRoleCode
belong: concepts
domain: 门户侧边栏查询
status: published
aliases:
  - roleCode
  - 授权角色编码
oid: 1

sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: CustCompanyFacade.getAuthRoleCode(companyType) 的返回值
adjudication: boundary
also_confused_with:
  - companyTypeCode
scope:
  databases: [lowcode_pplatform]
---

authRoleCode 是权限系统的角色编码，由企业角色编码 companyType 通过 CustCompanyFacade.getAuthRoleCode 转换得到。该概念用于区分业务企业角色与权限系统角色，两者通过映射关系关联。

## 需求背景

菜单查询链路 [[queryMenu-产品+企业角色菜单]] 中，必须先经过角色转换才能调用 RoleFacade.listMenuByRole。明确 authRoleCode 与 [[companyType]] 的边界，有助于理解权限过滤逻辑。

## 版本演进

当前转换逻辑封装在 Facade 中，若权限系统升级角色模型，需要重新评估映射规则。