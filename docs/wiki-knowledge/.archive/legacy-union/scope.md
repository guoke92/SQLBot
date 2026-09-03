---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:interworking-products@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 可见范围
page_key: scope
domain: 产品与配置
aliases:
- 全部可见
- 部分可见
- 适应范围
- 可见项目
anchors:
- scope
---
# 可见范围

tenant_interworking_product.scope：ALL=全部项目可见（tenant_interworking_project 无行）；SOME=部分可见（scopeProject JSON 数组指定项目，relTenantProject 先清后插逐项目建行，name=产品名-项目名）。scopeRole 另行控制哪些企业类型可见。

```ground:enum
enum: scope
fields:
- tenant_interworking_product.scope
values:
  ALL:
    label: 全部
  SOME:
    label: 指定范围
```

## 关联
- [[tenant_interworking_product|tenant_interworking_product]]
