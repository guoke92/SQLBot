---
type: table
title: 登录用户表 sys_user
page_key: table.sys_user
domain: 数据权限与组织
status: draft
aliases: [sys_user, 登录用户]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

系统登录用户表。组织树在渲染 createUser/updateUser 时，若名称缺失会按 createBy/updateBy 反查本表 name 填充；邮箱在业务邮箱变更时按条件同步更新 email。删除本表用户前需校验 [[tables/cust_user_rel]] 是否全部冻结，见 [[rules/sys_user_delete_all_products_frozen]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧组织树与邮箱同步链路。

## 版本演进

v0：依据 code 证据建档。

