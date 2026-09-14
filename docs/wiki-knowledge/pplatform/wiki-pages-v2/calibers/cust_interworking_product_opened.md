---
type: caliber
title: 口径：客户互通产品已开通
page_key: cust_interworking_product_opened
domain: 互通产品
status: draft
aliases: [客户互通产品已开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:cust_interworking_product
  - code:CustProductActiveConstant
contract_version: "0.1"
belong: calibers
---

判定 [[cust_interworking_product]] 中已开通的记录，取值为字符串 `OPENED`（[[CustProductActiveConstant]]），与租户侧的 `Y` 不通用，注意与 [[tenant_interworking_product_opened]] 区分。

## 需求背景
语义分析未附带需求文档锚点；客户侧开通完成以 OPENED 标记。

## 版本演进
语义分析未记录该口径的版本演进；DB 分布仅有 OPENED。

```ground:caliber
name: 客户互通产品已开通
predicate: "cust_interworking_product.open_status = 'OPENED'"
scope: cust_interworking_product
evidence: "db:CustProductActiveConstant.OPENED；DB 分布 OPENED"
```