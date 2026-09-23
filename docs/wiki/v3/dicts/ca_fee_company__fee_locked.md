---
type: dict
title: ca_fee_company.fee_locked
page_key: ca_fee_company__fee_locked
belong: dicts
status: draft
anchors:
- ca_fee_company.fee_locked
sources:
- database_profile:ca_fee_company.fee_locked
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- ca_fee_company
---
# ca_fee_company.fee_locked

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `ca_fee_company.fee_locked`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__fee_locked
fields:
- ca_fee_company.fee_locked
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
