---
type: rule
title: 租户产品唯一键约束
page_key: tenant_product_unique_key
domain: 租户产品
status: draft
aliases: [tenant_product_id, 租户产品唯一键]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product
contract_version: "0.1"
belong: rules
---

该约束规定 [[tables/tenant_product]] 中一个租户对同一平台产品只能有一条记录，是「租户产品」这一概念的建模基础，也是 [[concepts/platform_product_vs_tenant_product]] 中三级结构成立的前提。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。唯一键决定了重复开通时是幂等返回还是新增记录，配合 [[rules/activation_idempotency]] 一起理解。

## 版本演进
platform_product_id 上另有普通索引，唯一性由 tenant_id 组合保证；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 租户产品唯一键
table: tenant_product
fields: [tenant_id, platform_product_id]
statement: 租户 id 与 platform_product_id 组成唯一键 tenant_product_id
evidence: db
```