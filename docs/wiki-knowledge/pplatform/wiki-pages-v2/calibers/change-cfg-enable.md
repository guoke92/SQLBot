---
type: caliber
title: 生效变更配置
page_key: caliber.change-cfg-enable
domain: 企业变更与运营变更
status: draft
aliases: [配置有效标记, 变更配置查询口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
---

「生效变更配置」是 [[tables.cust_change_cfg]] 查询的基础过滤口径：只取 `enable = 'Y'` 的配置行。该口径是 [[calibers.change-cfg-match-dimensions]] 的组成部分，配置下线的标准做法是改标记而不是删行。

## 需求背景

变更项配置需要支持上下线而不丢失历史引用，因此以逻辑有效标记控制可见性；查询条件恒定携带该标记，保证任何入口拿到的都是生效配置。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.list`（`EnableEnum.Y.name()`）。

```ground:caliber
name: 生效变更配置
predicate: "cust_change_cfg.enable = 'Y'"
scope: 变更项配置查询
evidence: code_path:CustChangeApplication.java:list（EnableEnum.Y.name()）
```