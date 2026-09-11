---
type: rule
title: 租户产品开通幂等
page_key: rules/activation_idempotency
domain: 租户产品
status: draft
aliases: [开通幂等, activeAndNotify 幂等]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProductApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_product]] 已处于 Y（已开通）时，activeAndNotify 再次被调用直接返回，不重复推进状态、不重复通知。它是 [[processes/tenant_product_open_status]] 中 Y → Y 自环的依据，与唯一键约束 [[rules/tenant_product_unique_key]] 一致。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。多级回调场景下同一开通请求可能被重复投递，幂等是必要的保护。

## 版本演进
同一方法同时承担「非 ACFLOW/ORDER 直接开通」「ACFLOW/ORDER 置开通中」「已开通直接返回」三种分支，是产品线扩展后集中在一个入口的结果；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 租户产品开通幂等
table: tenant_product
fields: [open_status]
statement: activeAndNotify 幂等命中已开通直接返回
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:activeAndNotify"
```