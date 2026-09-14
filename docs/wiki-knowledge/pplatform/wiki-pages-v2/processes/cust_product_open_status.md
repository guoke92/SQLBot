---
type: process
title: 客户产品开通状态流转
page_key: cust_product_open_status
domain: 平台产品配置
status: draft
aliases: [客户产品开通状态, open_status 状态机]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustProductDomainService.java#initProduct
  - code:CustProductDomainService.java#doActiveProduct
  - code:CustProductDomainService.java#listTenantProductWithOpenedCustProduct
  - code:PlatFormProductProvierImpl.java#queryProductStatus
contract_version: "0.1"
belong: processes
---

客户产品开通状态刻画「企业 × 产品」的开通生命周期，落库于 [[cust_auth_application]] 的 `open_status`，取值为字面量常量类 `CustProductActiveConstant` 定义的 NOT_OPENED / OPENING / OPENED。该状态是客户端「我的产品 / 已开通产品」列表与进入产品校验的判活依据。

## 需求背景

三条口径 [[cust_product_not_opened]]、[[cust_product_opening]]、[[cust_product_opened]] 分别服务初始化开通、列表展示与判活/回退三类场景。需求文档对状态字面量的叙述（PENDING/ACTIVE/CANCEL）与实现不符，见 [[product_open_status]] 的边界裁定。

## 版本演进

- 常量类（非 Enum）承载写值点：`setOpenStatus(CustProductActiveConstant.OPENED/OPENING/NOT_OPENED)`，enum_audit 三项均 verdict=confirm。
- 「查无授权记录」会从 OPENED 语义回退为 NOT_OPENED，属展示层补位而非失败态。

```ground:process
name: 客户产品开通状态
field: cust_auth_application.open_status
states:
  - value: NOT_OPENED
    label: 未开通
    source: code_const
  - value: OPENING
    label: 开通中
    source: code_const
  - value: OPENED
    label: 已开通
    source: code_const
transitions:
  - from: NOT_OPENED
    event: initProduct 初始化客户产品
    to: OPENING
    evidence: "code_path:CustProductDomainService.java#initProduct"
  - from: OPENING
    event: doActiveProduct 开通完成
    to: OPENED
    evidence: "code_path:CustProductDomainService.java#doActiveProduct"
  - from: OPENED
    event: 查无授权记录回退
    to: NOT_OPENED
    evidence: "code_path:CustProductDomainService.java#listTenantProductWithOpenedCustProduct;PlatFormProductProvierImpl.java#queryProductStatus"
```

关联：[[cust_auth_application]]、[[tenant_product]]、[[cust_product_opened]]、[[cust_product_opening]]、[[cust_product_not_opened]]、[[product_open_status]]