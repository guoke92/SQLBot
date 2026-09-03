---
type: concept
title: isLeaf
page_key: isLeaf
domain: 门户侧边栏查询
status: published
aliases:
  - 叶子菜单
oid: 1

sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: SysMenuVO.subMenuList 为 null 或空时 true
adjudication: synonym
also_confused_with:
  - 菜单类型
scope:
  databases: [lowcode_pplatform]
---

isLeaf 是侧边栏菜单项是否叶子节点的布尔标记，其判定依据为 SysMenuVO.subMenuList 是否为 null 或空列表。该概念用于前端渲染菜单时判断是否展示子菜单。

## 需求背景

菜单扁平化规则 [[菜单扁平化与父子关联]] 中，叶子节点判定直接决定前端是否渲染展开图标。该概念避免将“菜单类型”字段与叶子判定混淆。

## 版本演进

当前判定仅基于子菜单列表是否为空，未考虑菜单类型（如按钮、目录），后续可结合类型字段优化。