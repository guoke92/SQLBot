---
type: caliber
title: 客户产品开通中
page_key: cust_product_opening
domain: 平台产品配置
status: draft
aliases: [开通中产品, OPENING]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「客户产品开通中」用于「我的产品」列表与初始化开通场景，标识记录已建立但尚未完成开通，等价于 [[cust_auth_application]] 的 `open_status = 'OPENING'`。

## 需求背景

开通中产品展示在列表中但不视为可用，待 [[cust_product_open_status]] 流转到 OPENED 后由 [[cust_product_opened]] 口径接管。

## 版本演进

- 初版口径，无历史变更。

```ground:caliber
name: 客户产品开通中
predicate: "cust_auth_application.open_status = 'OPENING'"
scope: 我的产品列表/初始化开通
evidence: code
```

关联：[[cust_auth_application]]、[[cust_product_open_status]]、[[cust_product_opened]]