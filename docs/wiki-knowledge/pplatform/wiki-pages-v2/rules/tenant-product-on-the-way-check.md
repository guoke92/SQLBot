---
type: rule
title: 租户产品在途校验
page_key: tenant-product-on-the-way-check
domain: 平台产品配置
status: draft
aliases: [在途校验, checkOnTheWay]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.checkOnTheWay
  - code:TenantProductDomainService.checkOnTheWay
contract_version: "0.1"
belong: rules
---

检查租户产品是否存在在途变更，如有则抛出异常，禁止激活。该规则是 [[processes/tenant-product-open-status]] 状态迁移（P→Y）的前置约束，字段落点为 [[tables/tenant_product]] 的 `open_status`。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `TenantProductApplication.checkOnTheWay` → `TenantProductDomainService.checkOnTheWay` 的调用链证据。

```ground:rule
name: 租户产品在途校验
content: "检查租户产品是否存在在途变更，如有则抛出异常，禁止激活。"
impact: "阻止激活操作。"
field_targets:
  - tenant_product.open_status
evidence: TenantProductApplication.checkOnTheWay -> TenantProductDomainService.checkOnTheWay
```

## 关联

- 表：[[tables/tenant_product]]
- 状态机：[[processes/tenant-product-open-status]]