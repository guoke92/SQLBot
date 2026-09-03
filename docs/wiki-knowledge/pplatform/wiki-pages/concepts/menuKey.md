---
type: concept
title: menuKey
page_key: menuKey
domain: 门户侧边栏查询
status: published
aliases:
  - code
  - 菜单编码
oid: 1

sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: SideBarMenuRes.menuKey = SysMenuVO.code
adjudication: synonym
also_confused_with:
  - menuId
scope:
  databases: [lowcode_pplatform]
---

menuKey 是侧边栏菜单项的唯一编码，其值为 SysMenuVO.code。与数据库关联使用的 menuId 不同，menuKey 面向前端展示和树结构还原。该概念用于澄清菜单编码与菜单 ID 的差异。

## 需求背景

在菜单扁平化与树形还原规则 [[菜单扁平化与父子关联]] 中，menuKey 和 parentMenuKey 分别使用 SysMenuVO.code 及其父节点 code，根节点 parentMenuKey 为 null。前端依赖 menuKey 标识菜单节点。

## 版本演进

当前 menuKey 直接取 SysMenuVO.code，若未来权限系统升级菜单编码规则，需要评估兼容性。