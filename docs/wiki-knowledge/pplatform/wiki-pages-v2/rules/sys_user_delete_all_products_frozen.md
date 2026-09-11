---
type: rule
title: 删除 sys 用户前须全部产品关系已冻结
page_key: rule.sys_user_delete_all_products_frozen
domain: 数据权限与组织
status: draft
aliases: [删除 sys 用户前置校验, is_freeze]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

删除 [[tables/sys_user]] 用户之前，必须校验该用户在所有产品上的关系记录是否均已冻结：[[tables/cust_user_rel]].is_freeze 为 'N' 表示未冻结，只有全部产品关系都冻结（无未冻结记录）才允许删除。该规则把「产品维度的冻结状态」作为「用户删除」的闸门，product_id 决定需要检查哪些业务系统。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 cust_user_rel 字段语义（「全部冻结才允许删除 sys 用户」）得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: sys 用户删除前置校验
statement: 只有用户全部产品关系均冻结时才允许删除 sys 用户
condition: 存在 is_freeze='N' 的产品关系
action: 拒绝删除 sys 用户
evidence: code_path:cust_user_rel.is_freeze（'N' 表示未冻结）
```