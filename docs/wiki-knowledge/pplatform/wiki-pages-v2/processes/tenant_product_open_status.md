---
type: process
title: 租户产品开通状态流转
page_key: tenant_product_open_status
domain: 租户产品
status: draft
aliases: [租户产品开通状态, tenant_product.open_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
  - code:TenantProductApplication
contract_version: "0.1"
belong: processes
---

描述 [[tenant_product]] 的 `open_status` 如何从"未开通"经过"开通中"到达"已开通"，以及取消开通的回退。取值定义见 [[ProductOpenStatusEnum]]，单态口径见 [[tenant_product_not_opened]]、[[tenant_product_opening]]、[[tenant_product_opened]]、[[valid_tenant_product]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：ACFLOW/ORDER 等产品为多级产品，开通需异步回调后置成功，因此必须有 `P`（开通中）中间态；非多级产品可直接由 N 到 Y。

## 版本演进
语义分析未记录该状态机的版本演进。

```ground:process
name: 租户产品开通状态
field: tenant_product.open_status
states:
  - value: N
    label: 未开通
    source: db_dist
  - value: P
    label: 开通中
    source: code_enum
  - value: Y
    label: 已开通
    source: db_dist
transitions:
  - from: N
    event: 开通ACFLOW/ORDER多级产品
    to: P
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:334"
  - from: P
    event: 多级回调后置成功
    to: Y
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: N
    event: 非多级产品直接生效
    to: Y
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
  - from: Y
    event: 取消开通产品
    to: N
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:cancel"
```