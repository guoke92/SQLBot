---
type: concept
title: parentMenuKey
page_key: parentMenuKey
belong: concepts
domain: 门户侧边栏查询
status: published
aliases:
  - parentId
oid: 1

sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: SideBarMenuRes.parentMenuKey = 父节点 SysMenuVO.code；根节点（parentId 为 0）时为 null
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

parentMenuKey 是侧边栏菜单响应中表示父菜单编码的字段，用于还原树形结构。根节点的 parentMenuKey 为 null，其他节点存储其父菜单的 SysMenuVO.code。

## 需求背景

由于菜单查询返回的是递归扁平化的列表（[[菜单扁平化与父子关联]]），前端需要 parentMenuKey 来重新构建父子层级。该概念明确了父编码的生成规则。

## 版本演进

当前依赖 parentId 为 0 判断根节点，若底层菜单表结构变化，需要同步调整。