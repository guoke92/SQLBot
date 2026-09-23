---
type: dict
title: ca_fee_company.renew_remind_sent
page_key: ca_fee_company__renew_remind_sent
belong: dicts
status: draft
anchors:
- ca_fee_company.renew_remind_sent
sources:
- database_profile:ca_fee_company.renew_remind_sent
- database_schema:ca_fee_company.renew_remind_sent
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- ca_fee_company
---
# ca_fee_company.renew_remind_sent

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `ca_fee_company.renew_remind_sent`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__renew_remind_sent
fields:
- ca_fee_company.renew_remind_sent
values:
  N:
    trust: proposed
    label: 未生成
  Y:
    trust: proposed
    label: 已生成
triage: keep
```
