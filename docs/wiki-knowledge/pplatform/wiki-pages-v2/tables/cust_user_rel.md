---
type: table
title: 用户产品关系表 cust_user_rel
page_key: table.cust_user_rel
domain: 数据权限与组织
status: draft
aliases: [cust_user_rel, 用户产品关系]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

用户与产品（业务系统）的关联表，决定经办人需要推送到哪些业务系统。is_freeze 是冻结标识，'N' 表示未冻结；删除 sys 用户前要求全部产品关系均已冻结，见 [[rules/sys_user_delete_all_products_frozen]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧冻结/删除校验链路。

## 版本演进

v0：依据 code 证据建档。

