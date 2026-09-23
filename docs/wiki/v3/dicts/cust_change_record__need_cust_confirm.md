---
type: dict
title: cust_change_record.need_cust_confirm
page_key: cust_change_record__need_cust_confirm
belong: dicts
status: draft
anchors:
- cust_change_record.need_cust_confirm
sources:
- database_profile:cust_change_record.need_cust_confirm
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- cust_change_record
---
# cust_change_record.need_cust_confirm

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `cust_change_record.need_cust_confirm`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__need_cust_confirm
fields:
- cust_change_record.need_cust_confirm
values:
  Y:
    trust: proposed
    label: 是
  N:
    trust: proposed
    label: 否
triage: keep
```
