---
type: caliber
title: 有效账户/有效记录口径
page_key: calibers/valid-record-enable-y
domain: 企业银行账户
status: draft
aliases: [逻辑删除口径, enable=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
---

有效记录指未被逻辑删除的数据行，判定条件为 `cust_account_info.enable = 'Y'`，作用域为该表通用逻辑删除口径。

## 需求背景

账户数据涉及历史与失效记录，物理删除会破坏认证与打款审计链路，因此统一以 enable 标记做逻辑删除，所有列表与取数默认叠加该过滤条件。与之相邻的状态字段（如 `status`，实测仅 INIT）不可替代本口径。

## 版本演进

v0 契约按现状固化，该口径适用于 [[tables/cust_account_info]] 全表查询。

## 口径锚点

```ground:caliber
name: 有效账户/有效记录
predicate: cust_account_info.enable = 'Y'
scope: 全表通用逻辑删除口径
evidence: db
```