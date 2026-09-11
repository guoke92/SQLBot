---
type: caliber
title: 有效联系人状态口径（status ∈ {ADD, EFFECT}）
page_key: caliber.person_effective_status
domain: 平台内部服务对接
status: draft
aliases:
  - 有效联系人
  - CustPersonStatusConstant
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.status]
contract_version: "0.1"
---

联系人没有沿用 enable 作为有效性判据，而是以状态枚举判定：查询有效联系人时取 ADD 或 EFFECT。

## 需求背景

该口径与企业的建档/生命周期状态机（[[processes/cust_build_status_machine]]、[[processes/cust_status_machine]]）不是同一套枚举，跨表统计时不可混用。联系人侧另有 cust_build_status 冗余字段，两者需区分。

## 版本演进

v0：首次成页。

```ground:caliber
name: 有效联系人状态口径
field: cust_person_info.status
values:
  - ADD
  - EFFECT
criterion: "查询有效联系人时取 ADD 或 EFFECT（CustPersonStatusConstant）"
evidence: code
```