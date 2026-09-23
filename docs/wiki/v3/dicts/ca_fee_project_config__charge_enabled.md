---
type: dict
title: ca_fee_project_config.charge_enabled
page_key: ca_fee_project_config__charge_enabled
belong: dicts
status: draft
anchors:
- ca_fee_project_config.charge_enabled
sources:
- database_profile:ca_fee_project_config.charge_enabled
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- ca_fee_project_config
---
# ca_fee_project_config.charge_enabled

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `ca_fee_project_config.charge_enabled`，表页 [[tables/ca_fee_project_config]]。

## 取值

```ground:dict
dict: ca_fee_project_config__charge_enabled
fields:
- ca_fee_project_config.charge_enabled
values:
  N:
    trust: proposed
    label: 停用
  Y:
    trust: proposed
    label: 启用
triage: keep
```
