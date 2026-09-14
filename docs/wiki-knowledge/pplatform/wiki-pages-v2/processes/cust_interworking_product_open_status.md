---
type: process
title: 客户互通产品开通状态
page_key: cust_interworking_product_open_status
domain: 互通产品
status: draft
aliases: [客户互通产品开通状态, cust_interworking_product.open_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustProductActiveConstant
  - db:cust_interworking_product
contract_version: "0.1"
belong: processes
---

描述 [[cust_interworking_product]] 的 `open_status` 取值集合（NOT_OPENED/OPENING/OPENED，见 [[CustProductActiveConstant]]）。语义分析未提供迁移事件，故本页只固化状态集合，口径见 [[cust_interworking_product_opened]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：客户侧开通存在"带客户确认 forams"的 OPENING 中间态。

## 版本演进
语义分析未记录该状态机的版本演进；DB 仅有 OPENED 分布。

```ground:process
name: 客户互通产品开通状态
field: cust_interworking_product.open_status
states:
  - value: NOT_OPENED
    label: 未开通
    source: code_enum
  - value: OPENING
    label: 开通中：带客户确认 forams
    source: code_enum
  - value: OPENED
    label: 已开通
    source: db_dist
transitions: []
```