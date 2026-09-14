---
type: process
title: 客户产品开通状态
page_key: cust-product-open-status
domain: 平台产品配置
status: draft
aliases: [客户产品开通状态机, cust_auth_application.open_status]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustProductDomainService.initProduct
  - code:CustProductDomainService.doActiveProduct
contract_version: "0.1"
belong: processes
---

客户产品开通状态描述 [[tables/cust_auth_application]] 中 `open_status` 的生命周期，取值为 OPENED/OPENING/NOT_OPENED 三态。初始化产品开通将状态置为「开通中」，激活动作既可从「开通中」进入「已开通」，也可从「未开通」直接进入「已开通」；「已开通」是 [[calibers/cust-open-product]] 口径的过滤条件。

激活动作与产品协议签署流程耦合，见 [[rules/product-agreement-activate]]。注意与租户侧三态枚举不可混用，辨析见 [[concepts/openStatus]]。

## 需求背景

语义分析未提供该状态机的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档。三条迁移均来自代码证据，其中 `activeProduct` 存在两条入边。

```ground:state_machine
name: 客户产品开通状态
field: cust_auth_application.open_status
states:
  - value: "OPENED"
    label: "已开通"
    source: code_enum
  - value: "OPENING"
    label: "开通中"
    source: code_enum
  - value: "NOT_OPENED"
    label: "未开通"
    source: code_enum
transitions:
  - from: "NOT_OPENED"
    event: initProduct
    to: "OPENING"
    evidence: CustProductDomainService.initProduct
  - from: "OPENING"
    event: activeProduct
    to: "OPENED"
    evidence: CustProductDomainService.doActiveProduct
  - from: "NOT_OPENED"
    event: activeProduct
    to: "OPENED"
    evidence: CustProductDomainService.doActiveProduct
```

## 关联

- 承载表：[[tables/cust_auth_application]]
- 租户侧对应状态机：[[processes/tenant-product-open-status]]
- 口径：[[calibers/cust-open-product]]
- 规则：[[rules/product-agreement-activate]]
- 术语：[[concepts/openStatus]]