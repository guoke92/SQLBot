---
type: dict
title: ca_certification_info.head_company_data
page_key: ca_certification_info__head_company_data
belong: dicts
status: draft
anchors:
- ca_certification_info.head_company_data
sources:
- database_profile:ca_certification_info.head_company_data
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- ca_certification_info
---
# ca_certification_info.head_company_data

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `ca_certification_info.head_company_data`，表页 [[tables/ca_certification_info]]。

## 取值

```ground:dict
dict: ca_certification_info__head_company_data
fields:
- ca_certification_info.head_company_data
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
