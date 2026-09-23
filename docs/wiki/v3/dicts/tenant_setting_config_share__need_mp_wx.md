---
type: dict
title: tenant_setting_config_share.need_mp_wx
page_key: tenant_setting_config_share__need_mp_wx
belong: dicts
status: draft
anchors:
- tenant_setting_config_share.need_mp_wx
sources:
- database_profile:tenant_setting_config_share.need_mp_wx
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- tenant_setting_config_share
---
# tenant_setting_config_share.need_mp_wx

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `tenant_setting_config_share.need_mp_wx`，表页 [[tables/tenant_setting_config_share]]。

## 取值

```ground:dict
dict: tenant_setting_config_share__need_mp_wx
fields:
- tenant_setting_config_share.need_mp_wx
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
