---
type: dict
title: tenant_setting_config.project_code_required
page_key: tenant_setting_config__project_code_required
belong: dicts
status: draft
anchors:
- tenant_setting_config.project_code_required
sources:
- database_profile:tenant_setting_config.project_code_required
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- tenant_setting_config
---
# tenant_setting_config.project_code_required

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `tenant_setting_config.project_code_required`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__project_code_required
fields:
- tenant_setting_config.project_code_required
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
