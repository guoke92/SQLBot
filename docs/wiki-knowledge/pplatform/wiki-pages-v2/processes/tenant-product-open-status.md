---
type: process
title: 租户产品开通状态
page_key: tenant-product-open-status
domain: 平台产品配置
status: draft
aliases: [租户产品开通状态机, tenant_product.open_status]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.activeAndNotify
  - code:TenantProductApplication.cancel
contract_version: "0.1"
belong: processes
---

租户产品开通状态描述 [[tables/tenant_product]] 中 `open_status` 的生命周期，取值为 Y/P/N 三态。租户产品从「开通中」经激活动作进入「已开通」，已开通产品可被取消回到「未开通/取消」。该状态是租户侧产品可见性的判定基础，也是 [[calibers/tenant-open-product]] 口径的过滤字段。

激活前存在在途校验约束，见 [[rules/tenant-product-on-the-way-check]]；与客户侧状态枚举的差异辨析见 [[concepts/openStatus]]。

## 需求背景

语义分析未提供该状态机的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档。两个迁移动作 `activeAndNotify`、`cancel` 均来自代码证据。

```ground:state_machine
name: 租户产品开通状态
field: tenant_product.open_status
states:
  - value: "Y"
    label: "已开通"
    source: code_enum
  - value: "P"
    label: "开通中"
    source: code_enum
  - value: "N"
    label: "未开通/取消"
    source: code_enum
transitions:
  - from: "P"
    event: activeAndNotify
    to: "Y"
    evidence: TenantProductApplication.activeAndNotify
  - from: "Y"
    event: cancel
    to: "N"
    evidence: TenantProductApplication.cancel
```

## 关联

- 承载表：[[tables/tenant_product]]
- 客户侧对应状态机：[[processes/cust-product-open-status]]
- 口径：[[calibers/tenant-open-product]]
- 规则：[[rules/tenant-product-on-the-way-check]]
- 术语：[[concepts/openStatus]]