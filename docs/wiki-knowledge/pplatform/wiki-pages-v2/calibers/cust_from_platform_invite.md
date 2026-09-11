---
type: caliber
title: 客户来源空值口径（邀请类认证写「平台邀请」）
page_key: caliber.cust_from_platform_invite
domain: 平台内部服务对接
status: draft
aliases:
  - 平台邀请
  - cust_from 口径
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.cust_from]
  - semantic:field_semantics[cust_company_info.cust_source]
contract_version: "0.1"
---

客户来源在邀请类认证（客户录入/平台录入）且原值为空时，统一补写为「平台邀请」。

## 需求背景

cust_from 与 cust_source 语义不同：前者是业务来源描述（可为「平台邀请」），后者是渠道标识（如 PLATFORM_PUSH）。统计来源分布时应先明确取哪一列。

## 版本演进

v0：首次成页。

```ground:caliber
name: 客户来源空值口径
field: cust_company_info.cust_from
values:
  - "平台邀请"
criterion: "邀请类认证为空时写 \"平台邀请\""
related_fields:
  - cust_company_info.cust_source
evidence: code
```